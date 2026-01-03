import React, { useState, useRef } from 'react';
import '../styles/FileUpload.css';

function FileUpload({ onFileUpload, loading }) {
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = e.dataTransfer.files;
    addFiles(droppedFiles);
  };

  const addFiles = (newFiles) => {
    const fileArray = Array.from(newFiles).filter((file) => file.name.endsWith('.bz2'));
    
    if (fileArray.length === 0) {
      alert('Please select BZip2 compressed files (.bz2)');
      return;
    }

    setFiles((prev) => [...prev, ...fileArray]);
  };

  const handleFileSelect = (e) => {
    addFiles(e.target.files);
  };

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert('Please select at least one file');
      return;
    }

    onFileUpload(files);
    setFiles([]);
  };

  const totalSize = files.reduce((sum, file) => sum + file.size, 0);
  const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2);

  return (
    <div className="file-upload">
      <div className="upload-header">
        <h1>Upload Betfair Files</h1>
        <p>Upload BZip2-compressed Betfair historical data files for parsing</p>
      </div>

      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="drop-zone-content">
          <div className="drop-icon">📥</div>
          <h2>Drag files here or click to browse</h2>
          <p>Accepted format: BZip2 compressed files (.bz2)</p>
          <button
            className="btn btn-primary"
            onClick={() => fileInputRef.current?.click()}
            disabled={loading}
          >
            Browse Files
          </button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".bz2"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
        disabled={loading}
      />

      {files.length > 0 && (
        <div className="upload-section">
          <div className="section-header">
            <h2>Selected Files ({files.length})</h2>
            <div className="section-stats">
              <span>Total size: {totalSizeMB} MB</span>
            </div>
          </div>

          <div className="file-queue">
            {files.map((file, index) => (
              <div key={index} className="queue-item">
                <div className="queue-info">
                  <div className="queue-icon">🗂️</div>
                  <div className="queue-details">
                    <div className="queue-name">{file.name}</div>
                    <div className="queue-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                  </div>
                </div>
                <button
                  className="btn-remove"
                  onClick={() => handleRemoveFile(index)}
                  disabled={loading}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <div className="upload-actions">
            <button
              className="btn btn-secondary"
              onClick={() => setFiles([])}
              disabled={loading}
            >
              Clear All
            </button>
            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={loading || files.length === 0}
            >
              {loading ? 'Uploading...' : 'Upload Files'}
            </button>
          </div>
        </div>
      )}

      <div className="upload-info">
        <h3>📋 File Requirements</h3>
        <ul>
          <li>Format: BZip2 compressed (.bz2)</li>
          <li>Maximum size: 500 MB per file</li>
          <li>Content: Betfair historical market or event data</li>
          <li>Source: Downloaded from historicdata.betfair.com</li>
        </ul>
      </div>

      <div className="upload-tips">
        <h3>💡 Tips</h3>
        <ul>
          <li>Download historical data from <a href="https://historicdata.betfair.com" target="_blank" rel="noopener noreferrer">Betfair Historic Data</a></li>
          <li>Keep files in BZip2 format (do not extract)</li>
          <li>Multiple files can be uploaded at once</li>
          <li>View uploaded files in the Dashboard or File Viewer</li>
        </ul>
      </div>
    </div>
  );
}

export default FileUpload;
