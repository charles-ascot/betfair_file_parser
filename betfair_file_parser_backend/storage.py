"""
Storage backends for Betfair File Parser

Provides two storage implementations:
- FileStore: In-memory storage for local development
- CloudFileStore: Google Cloud Storage + Firestore for production
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseFileStore(ABC):
    """Abstract base class for file storage backends"""

    @abstractmethod
    def save(self, file_id: str, data: Dict[str, Any]) -> None:
        """Save file data"""
        pass

    @abstractmethod
    def get(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file data by ID"""
        pass

    @abstractmethod
    def delete(self, file_id: str) -> None:
        """Delete file by ID"""
        pass

    @abstractmethod
    def list_files(self) -> List[Dict[str, Any]]:
        """List all files (metadata only)"""
        pass


class FileStore(BaseFileStore):
    """In-memory file storage for local development"""

    def __init__(self):
        self.files: Dict[str, Dict[str, Any]] = {}
        self.temp_dir = tempfile.gettempdir()

    def save(self, file_id: str, data: Dict[str, Any]) -> None:
        self.files[file_id] = data

    def get(self, file_id: str) -> Optional[Dict[str, Any]]:
        return self.files.get(file_id)

    def delete(self, file_id: str) -> None:
        if file_id in self.files:
            del self.files[file_id]

    def list_files(self) -> List[Dict[str, Any]]:
        return list(self.files.values())


class CloudFileStore(BaseFileStore):
    """
    Cloud-based file storage using Google Cloud Storage + Firestore

    - Firestore: Stores file metadata for fast queries
    - Cloud Storage: Stores full parsed JSON data
    """

    def __init__(self, bucket_name: str, project_id: Optional[str] = None):
        from google.cloud import storage, firestore

        self.bucket_name = bucket_name
        self.project_id = project_id

        # Initialize clients
        self.storage_client = storage.Client(project=project_id)
        self.firestore_client = firestore.Client(project=project_id)

        # Get bucket reference
        self.bucket = self.storage_client.bucket(bucket_name)

        # Firestore collection for file metadata
        self.collection = self.firestore_client.collection("files")

        logger.info(f"CloudFileStore initialized with bucket: {bucket_name}")

    def _get_gcs_path(self, file_id: str) -> str:
        """Get Cloud Storage path for a file"""
        return f"files/{file_id}/parsed_data.json"

    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from full file data for Firestore storage"""
        file_metadata = data.get("file_metadata", {})
        processing_stats = data.get("processing_stats", {})
        markets = data.get("markets", [])

        return {
            "file_id": file_metadata.get("file_id"),
            "file_name": file_metadata.get("file_name"),
            "size_bytes": file_metadata.get("size_bytes"),
            "upload_time": file_metadata.get("upload_time"),
            "processing_status": file_metadata.get("processing_status"),
            "processed_at": file_metadata.get("processed_at"),
            "error_message": file_metadata.get("error_message"),
            "total_markets": len(markets),
            "total_runners": processing_stats.get("total_runners", 0),
            "processing_time_ms": processing_stats.get("processing_time_ms", 0),
            "compressed_size_bytes": processing_stats.get("compressed_size_bytes", 0),
            "decompressed_size_bytes": processing_stats.get("decompressed_size_bytes", 0),
            "gcs_path": self._get_gcs_path(file_metadata.get("file_id", "")),
        }

    def save(self, file_id: str, data: Dict[str, Any]) -> None:
        """
        Save file data to Cloud Storage and metadata to Firestore

        1. Upload full JSON to Cloud Storage
        2. Save metadata to Firestore
        """
        gcs_path = self._get_gcs_path(file_id)

        try:
            # Upload full data to Cloud Storage
            blob = self.bucket.blob(gcs_path)
            json_data = json.dumps(data, default=str)
            blob.upload_from_string(
                json_data,
                content_type="application/json"
            )
            logger.info(f"Uploaded file data to gs://{self.bucket_name}/{gcs_path}")

            # Save metadata to Firestore
            metadata = self._extract_metadata(data)
            self.collection.document(file_id).set(metadata)
            logger.info(f"Saved metadata to Firestore for file_id: {file_id}")

        except Exception as e:
            # Cleanup on failure: delete GCS blob if Firestore save failed
            logger.error(f"Error saving file {file_id}: {e}")
            try:
                blob = self.bucket.blob(gcs_path)
                if blob.exists():
                    blob.delete()
            except Exception:
                pass
            raise

    def get(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file data from Cloud Storage

        1. Check Firestore for metadata (fast check if file exists)
        2. Download full data from Cloud Storage
        """
        try:
            # Check if file exists in Firestore
            doc = self.collection.document(file_id).get()
            if not doc.exists:
                logger.debug(f"File not found in Firestore: {file_id}")
                return None

            # Download full data from Cloud Storage
            metadata = doc.to_dict()
            gcs_path = metadata.get("gcs_path", self._get_gcs_path(file_id))

            blob = self.bucket.blob(gcs_path)
            if not blob.exists():
                logger.warning(f"File exists in Firestore but not in GCS: {file_id}")
                return None

            json_data = blob.download_as_string()
            data = json.loads(json_data)
            logger.debug(f"Retrieved file data for: {file_id}")
            return data

        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {e}")
            return None

    def delete(self, file_id: str) -> None:
        """
        Delete file from both Cloud Storage and Firestore
        """
        gcs_path = self._get_gcs_path(file_id)

        try:
            # Delete from Cloud Storage
            blob = self.bucket.blob(gcs_path)
            if blob.exists():
                blob.delete()
                logger.info(f"Deleted from GCS: gs://{self.bucket_name}/{gcs_path}")

            # Delete from Firestore
            self.collection.document(file_id).delete()
            logger.info(f"Deleted from Firestore: {file_id}")

        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise

    def list_files(self) -> List[Dict[str, Any]]:
        """
        List all files from Firestore (metadata only)

        This is fast because we only query Firestore, not Cloud Storage
        """
        try:
            docs = self.collection.stream()
            files = []

            for doc in docs:
                metadata = doc.to_dict()
                # Reconstruct the structure expected by the API
                files.append({
                    "file_metadata": {
                        "file_id": metadata.get("file_id"),
                        "file_name": metadata.get("file_name"),
                        "size_bytes": metadata.get("size_bytes"),
                        "upload_time": metadata.get("upload_time"),
                        "processing_status": metadata.get("processing_status"),
                        "processed_at": metadata.get("processed_at"),
                        "error_message": metadata.get("error_message"),
                    },
                    "processing_stats": {
                        "total_records": metadata.get("total_markets", 0),
                        "total_runners": metadata.get("total_runners", 0),
                        "processing_time_ms": metadata.get("processing_time_ms", 0),
                        "compressed_size_bytes": metadata.get("compressed_size_bytes", 0),
                        "decompressed_size_bytes": metadata.get("decompressed_size_bytes", 0),
                    },
                    "markets": [],  # Don't load full market data for listing
                })

            logger.debug(f"Listed {len(files)} files from Firestore")
            return files

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []


def create_file_store() -> BaseFileStore:
    """
    Factory function to create the appropriate file store based on environment

    Set USE_CLOUD_STORAGE=true and GCS_BUCKET_NAME to use cloud storage
    """
    use_cloud = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if use_cloud and bucket_name:
        logger.info("Using CloudFileStore for persistent storage")
        return CloudFileStore(bucket_name=bucket_name, project_id=project_id)
    else:
        logger.info("Using in-memory FileStore (data will not persist)")
        return FileStore()
