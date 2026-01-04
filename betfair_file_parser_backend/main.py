"""
Betfair File Parser - Backend API
FastAPI application for parsing and visualizing Betfair historical data
"""

import os
import sys
import logging
import uuid
import json
import bz2
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import betfairlightweight
from betfairlightweight.streaming import StreamListener

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class FileMetadata(BaseModel):
    file_id: str
    file_name: str
    size_bytes: int
    upload_time: str
    processing_status: str
    error_message: Optional[str] = None
    processed_at: Optional[str] = None

class RunnerBSP(BaseModel):
    near_price: Optional[float] = None
    far_price: Optional[float] = None
    actual_sp: Optional[float] = None
    back_stake_taken: List[List[float]] = []
    lay_liability_taken: List[List[float]] = []

class RunnerEX(BaseModel):
    available_to_back: List[List[float]] = []
    available_to_lay: List[List[float]] = []
    traded_volume: List[List[float]] = []

class Runner(BaseModel):
    selection_id: int
    runner_name: str
    status: str
    bsp: RunnerBSP
    ex: RunnerEX
    last_price_traded: Optional[float] = None
    adjustment_factor: Optional[float] = None

class Market(BaseModel):
    market_id: str
    market_name: str
    market_type: str
    event_id: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[str] = None
    country_code: Optional[str] = None
    market_status: str
    inplay: bool
    total_matched: float
    total_available: float
    number_of_runners: int
    number_of_winners: int
    publish_time: Optional[str] = None
    version: Optional[int] = None
    runners: List[Runner] = []

class ProcessingStats(BaseModel):
    total_records: int
    total_runners: int
    processing_time_ms: int
    compressed_size_bytes: int
    decompressed_size_bytes: int

class FileParseResponse(BaseModel):
    file_metadata: FileMetadata
    markets: List[Market]
    processing_stats: ProcessingStats

class ExportRequest(BaseModel):
    format: str  # 'csv' or 'json'
    include_prices: bool = True
    runner_filter: Optional[List[int]] = None

class UploadResponse(BaseModel):
    file_id: str
    file_name: str
    status: str
    size_bytes: int

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str

# ============================================================================
# File Storage (Cloud Storage + Firestore in production, in-memory for local dev)
# ============================================================================

from storage import create_file_store

file_store = create_file_store()

# ============================================================================
# Betfair Data Parser
# ============================================================================

class BetfairDataParser:
    """Parse Betfair historical BZip2 compressed files"""
    
    @staticmethod
    def decompress_bz2(file_content: bytes) -> str:
        """Decompress BZip2 content to string"""
        try:
            decompressed = bz2.decompress(file_content)
            return decompressed.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decompress BZip2: {str(e)}")
            raise ValueError(f"Failed to decompress file: {str(e)}")
    
    @staticmethod
    def parse_json_stream(content: str) -> List[Dict[str, Any]]:
        """Parse JSON stream (line-delimited JSON)"""
        records = []
        for line in content.strip().split('\n'):
            if line.strip():
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipped invalid JSON line: {str(e)}")
                    continue
        return records
    
    @staticmethod
    def extract_market_data(stream_data: Dict[str, Any]) -> Market:
        """Extract market data from Betfair stream record"""
        
        # Market-level fields
        market_id = stream_data.get('mc', [{}])[0].get('id', 'UNKNOWN')
        market_definition = stream_data.get('marketDefinition', {})
        market_name = market_definition.get('name', 'Unknown Market')
        market_type = market_definition.get('marketType', 'UNKNOWN')
        event = market_definition.get('event', {})
        event_id = event.get('id', '')
        event_name = event.get('name', '')
        event_date = event.get('openDate', '')
        country_code = event.get('countryCode', '')
        
        market_catalogue = stream_data.get('marketCatalogue', {})
        if not market_name or market_name == 'Unknown Market':
            market_name = market_catalogue.get('marketName', market_name)
        
        # Market book data
        market_book = stream_data.get('mc', [{}])[0]
        market_status = market_definition.get('status', 'UNKNOWN')
        inplay = market_definition.get('inPlay', False)
        total_matched = market_book.get('tv', 0.0)  # total volume
        total_available = market_book.get('totalAvailable', 0.0)
        
        # Runner information
        runners = []
        runner_books = market_book.get('runners', [])
        
        for runner_book in runner_books:
            selection_id = runner_book.get('id')
            status = runner_book.get('status', 'ACTIVE')
            
            # Get runner name from market catalogue
            runner_name = 'Unknown'
            runner_catalogue = market_catalogue.get('runners', [])
            for rc in runner_catalogue:
                if rc.get('selectionId') == selection_id:
                    runner_name = rc.get('runnerName', 'Unknown')
                    break
            
            # BSP data
            bsp_data = runner_book.get('sp', {})
            bsp = RunnerBSP(
                near_price=bsp_data.get('n'),
                far_price=bsp_data.get('f'),
                actual_sp=bsp_data.get('l'),
                back_stake_taken=BetfairDataParser._format_price_stakes(
                    bsp_data.get('bst', [])
                ),
                lay_liability_taken=BetfairDataParser._format_price_stakes(
                    bsp_data.get('lst', [])
                )
            )
            
            # Exchange (EX) data
            ex_data = runner_book.get('ex', {})
            ex = RunnerEX(
                available_to_back=BetfairDataParser._format_price_stakes(
                    ex_data.get('atb', [])
                ),
                available_to_lay=BetfairDataParser._format_price_stakes(
                    ex_data.get('atl', [])
                ),
                traded_volume=BetfairDataParser._format_price_stakes(
                    ex_data.get('tv', [])
                )
            )
            
            last_price_traded = runner_book.get('ltp')
            adjustment_factor = runner_book.get('adjustmentFactor', 1.0)
            
            runner = Runner(
                selection_id=selection_id,
                runner_name=runner_name,
                status=status,
                bsp=bsp,
                ex=ex,
                last_price_traded=last_price_traded,
                adjustment_factor=adjustment_factor
            )
            runners.append(runner)
        
        market = Market(
            market_id=market_id,
            market_name=market_name,
            market_type=market_type,
            event_id=event_id,
            event_name=event_name,
            event_date=event_date,
            country_code=country_code,
            market_status=market_status,
            inplay=inplay,
            total_matched=total_matched,
            total_available=total_available,
            number_of_runners=len(runners),
            number_of_winners=market_definition.get('numberOfWinners', 1),
            publish_time=stream_data.get('publishTime'),
            version=stream_data.get('version'),
            runners=runners
        )
        
        return market
    
    @staticmethod
    def _format_price_stakes(raw_data: List) -> List[List[float]]:
        """Format raw price/stake data"""
        if not raw_data:
            return []
        # Each item is typically [price, stake/volume]
        return [list(item) if isinstance(item, (list, tuple)) else [float(item), 0.0] 
                for item in raw_data]
    
    @classmethod
    def parse_file(cls, file_content: bytes, file_name: str) -> FileParseResponse:
        """Parse complete Betfair file and return structured data"""
        
        import time
        start_time = time.time()
        compressed_size = len(file_content)
        
        # Decompress
        try:
            decompressed_content = cls.decompress_bz2(file_content)
        except ValueError as e:
            raise ValueError(f"Decompression failed: {str(e)}")
        
        decompressed_size = len(decompressed_content.encode('utf-8'))
        
        # Parse JSON stream
        try:
            records = cls.parse_json_stream(decompressed_content)
        except Exception as e:
            raise ValueError(f"JSON parsing failed: {str(e)}")
        
        if not records:
            raise ValueError("No valid records found in file")
        
        # Extract market data from first record (MVP approach)
        # In production, could aggregate multiple markets
        markets = []
        total_runners = 0
        
        try:
            # Try to parse as market data
            for record in records:
                try:
                    market = cls.extract_market_data(record)
                    markets.append(market)
                    total_runners += len(market.runners)
                except Exception as e:
                    logger.warning(f"Failed to parse record: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Market extraction failed: {str(e)}")
            raise ValueError(f"Failed to extract market data: {str(e)}")
        
        if not markets:
            raise ValueError("No valid markets found in file")
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        file_metadata = FileMetadata(
            file_id=str(uuid.uuid4()),
            file_name=file_name,
            size_bytes=compressed_size,
            upload_time=datetime.utcnow().isoformat() + 'Z',
            processing_status='completed',
            processed_at=datetime.utcnow().isoformat() + 'Z'
        )
        
        processing_stats = ProcessingStats(
            total_records=len(records),
            total_runners=total_runners,
            processing_time_ms=processing_time_ms,
            compressed_size_bytes=compressed_size,
            decompressed_size_bytes=decompressed_size
        )
        
        return FileParseResponse(
            file_metadata=file_metadata,
            markets=markets,
            processing_stats=processing_stats
        )

# ============================================================================
# Export Functions
# ============================================================================

class DataExporter:
    """Export parsed data to various formats"""
    
    @staticmethod
    def to_csv(markets: List[Market], include_prices: bool = True) -> str:
        """Export to CSV format"""
        lines = []
        
        # Header
        if include_prices:
            header = "Market ID,Market Name,Event Name,Runner ID,Runner Name,Status," \
                     "Last Traded,Near Price,Far Price,Actual SP,Back Vol,Lay Vol"
        else:
            header = "Market ID,Market Name,Event Name,Runner ID,Runner Name,Status"
        
        lines.append(header)
        
        # Data rows
        for market in markets:
            for runner in market.runners:
                if include_prices:
                    back_vol = sum([stake for _, stake in runner.ex.available_to_back])
                    lay_vol = sum([stake for _, stake in runner.ex.available_to_lay])
                    
                    row = f'{market.market_id},{market.market_name},{market.event_name},' \
                          f'{runner.selection_id},{runner.runner_name},{runner.status},' \
                          f'{runner.last_price_traded or ""},' \
                          f'{runner.bsp.near_price or ""},' \
                          f'{runner.bsp.far_price or ""},' \
                          f'{runner.bsp.actual_sp or ""},' \
                          f'{back_vol},{lay_vol}'
                else:
                    row = f'{market.market_id},{market.market_name},{market.event_name},' \
                          f'{runner.selection_id},{runner.runner_name},{runner.status}'
                
                lines.append(row)
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_json(data: FileParseResponse, pretty: bool = True) -> str:
        """Export to JSON format"""
        data_dict = data.dict()
        if pretty:
            return json.dumps(data_dict, indent=2)
        else:
            return json.dumps(data_dict)

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Betfair File Parser API",
    description="Parse and visualize Betfair historical data files",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "betfair-file-parser",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

@app.get("/status")
async def get_status():
    """Get service status and statistics"""
    return {
        "status": "operational",
        "files_processed": len(file_store.files),
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

# ============================================================================
# File Operations Endpoints
# ============================================================================

@app.post("/api/files/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse a Betfair file"""
    
    file_id = str(uuid.uuid4())
    
    try:
        # Read file
        content = await file.read()
        
        # Validate file
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        if len(content) > 500 * 1024 * 1024:  # 500MB limit
            raise HTTPException(status_code=413, detail="File too large (max 500MB)")
        
        # Check for BZip2 magic bytes
        if not content.startswith(b'BZ'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Expected BZip2 compressed file (.bz2)"
            )
        
        # Parse file
        try:
            parse_result = BetfairDataParser.parse_file(content, file.filename)
            
            # Store parsed data
            file_store.save(file_id, parse_result.dict())
            
            logger.info(f"File {file_id} parsed successfully: {file.filename}")
            
            return UploadResponse(
                file_id=file_id,
                file_name=file.filename,
                status="completed",
                size_bytes=len(content)
            )
        
        except ValueError as e:
            logger.error(f"Parsing failed for {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Parsing error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error parsing {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")

@app.get("/api/files/{file_id}", response_model=FileParseResponse)
async def get_file_data(file_id: str):
    """Get parsed data for a file"""
    
    file_data = file_store.get(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileParseResponse(**file_data)

@app.get("/api/files")
async def list_files():
    """List all uploaded files"""
    
    files = file_store.list_files()
    return {
        "count": len(files),
        "files": [
            {
                "file_id": f["file_metadata"]["file_id"],
                "file_name": f["file_metadata"]["file_name"],
                "size_bytes": f["file_metadata"]["size_bytes"],
                "upload_time": f["file_metadata"]["upload_time"],
                "status": f["file_metadata"]["processing_status"],
                "markets": len(f.get("markets", []))
            }
            for f in files
        ]
    }

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file and its parsed data"""
    
    if not file_store.get(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    
    file_store.delete(file_id)
    return {"message": "File deleted", "file_id": file_id}

# ============================================================================
# Export Endpoints
# ============================================================================

@app.post("/api/files/{file_id}/export")
async def export_file(file_id: str, request: ExportRequest):
    """Export file data in specified format"""
    
    file_data = file_store.get(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        parse_result = FileParseResponse(**file_data)
        
        if request.format.lower() == 'csv':
            content = DataExporter.to_csv(parse_result.markets, request.include_prices)
            media_type = "text/csv"
            filename = f"{file_id}.csv"
        
        elif request.format.lower() == 'json':
            content = DataExporter.to_json(parse_result, pretty=True)
            media_type = "application/json"
            filename = f"{file_id}.json"
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Export failed for {file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Export failed")

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow().isoformat() + 'Z'
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            timestamp=datetime.utcnow().isoformat() + 'Z'
        ).dict()
    )

# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Betfair File Parser API starting up")
    if hasattr(file_store, 'temp_dir'):
        logger.info(f"Temporary storage: {file_store.temp_dir}")
    else:
        logger.info("Using Cloud Storage backend")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Betfair File Parser API shutting down")

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
