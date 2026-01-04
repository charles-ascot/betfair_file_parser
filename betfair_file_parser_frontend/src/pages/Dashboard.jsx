import React from 'react';
import '../styles/Dashboard.css';

function Dashboard({ files, onViewFile, onDeleteFile, onDeleteAll }) {
  const totalFiles = files.length;
  const totalMarkets = files.reduce((sum, f) => sum + (f.markets || 0), 0);

  const recentFiles = files.slice(0, 5);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome to Betfair File Parser. Upload, parse, and export Betfair historical data.</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <div className="stat-label">Files Uploaded</div>
            <div className="stat-value">{totalFiles}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Total Markets</div>
            <div className="stat-value">{totalMarkets}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-label">API Status</div>
            <div className="stat-value">Active</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-label">Success Rate</div>
            <div className="stat-value">100%</div>
          </div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Quick Start</h2>
        <div className="quick-start-cards">
          <div className="quick-start-card">
            <div className="qs-number">1</div>
            <h3>Upload File</h3>
            <p>Download Betfair data and upload BZip2-compressed files (.bz2)</p>
          </div>
          <div className="quick-start-card">
            <div className="qs-number">2</div>
            <h3>View Data</h3>
            <p>Explore parsed market data with all field names and values</p>
          </div>
          <div className="quick-start-card">
            <div className="qs-number">3</div>
            <h3>Export</h3>
            <p>Export to CSV or JSON for analysis in your tools</p>
          </div>
        </div>
      </div>

      {recentFiles.length > 0 && (
        <div className="dashboard-section">
          <div className="section-header">
            <h2>Recent Files</h2>
            <button className="btn btn-danger" onClick={onDeleteAll}>
              Delete All Files
            </button>
          </div>
          <div className="file-list">
            {recentFiles.map((file) => (
              <div key={file.file_id} className="file-item">
                <div className="file-info">
                  <div className="file-name">{file.file_name}</div>
                  <div className="file-details">
                    <span>📦 {file.size_bytes} bytes</span>
                    <span>📊 {file.markets} markets</span>
                    <span>📅 {new Date(file.upload_time).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="file-actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => onViewFile(file.file_id)}
                  >
                    View
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => onDeleteFile(file.file_id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {totalFiles === 0 && (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Files Yet</h3>
          <p>Upload a Betfair historical data file to get started</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
