import React, { useState, useEffect } from 'react';
import '../styles/FileViewer.css';

function FileViewer({ fileId, apiBaseUrl, onDelete, onExport }) {
  const [fileData, setFileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedRunners, setExpandedRunners] = useState(new Set());

  useEffect(() => {
    if (fileId) {
      loadFile();
    }
  }, [fileId]);

  const loadFile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/api/files/${fileId}`);
      if (response.ok) {
        const data = await response.json();
        setFileData(data);
        setError(null);
      } else {
        setError('Failed to load file');
      }
    } catch (err) {
      console.error('Error loading file:', err);
      setError('Failed to load file data');
    } finally {
      setLoading(false);
    }
  };

  const toggleRunner = (runnerId) => {
    const newExpanded = new Set(expandedRunners);
    if (newExpanded.has(runnerId)) {
      newExpanded.delete(runnerId);
    } else {
      newExpanded.add(runnerId);
    }
    setExpandedRunners(newExpanded);
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!fileData) {
    return <div className="error-message">No file data available</div>;
  }

  const { file_metadata, markets, processing_stats } = fileData;

  return (
    <div className="file-viewer">
      <div className="viewer-header">
        <h1>File Viewer</h1>
        <p>{file_metadata.file_name}</p>
      </div>

      <div className="metadata-panel">
        <h2>File Metadata</h2>
        <div className="metadata-grid">
          <div className="metadata-item">
            <label>File Name</label>
            <value>{file_metadata.file_name}</value>
          </div>
          <div className="metadata-item">
            <label>File Size</label>
            <value>{(file_metadata.size_bytes / 1024 / 1024).toFixed(2)} MB</value>
          </div>
          <div className="metadata-item">
            <label>Upload Time</label>
            <value>{new Date(file_metadata.upload_time).toLocaleString()}</value>
          </div>
          <div className="metadata-item">
            <label>Status</label>
            <value>{file_metadata.processing_status}</value>
          </div>
        </div>
      </div>

      <div className="stats-panel">
        <h2>Processing Statistics</h2>
        <div className="stats-grid">
          <div className="stat">
            <label>Total Records</label>
            <value>{processing_stats.total_records}</value>
          </div>
          <div className="stat">
            <label>Total Runners</label>
            <value>{processing_stats.total_runners}</value>
          </div>
          <div className="stat">
            <label>Processing Time</label>
            <value>{processing_stats.processing_time_ms}ms</value>
          </div>
          <div className="stat">
            <label>Compression Ratio</label>
            <value>{((1 - processing_stats.compressed_size_bytes / processing_stats.decompressed_size_bytes) * 100).toFixed(1)}%</value>
          </div>
        </div>
      </div>

      <div className="markets-panel">
        <h2>Markets ({markets.length})</h2>
        {markets.map((market, marketIndex) => (
          <div key={marketIndex} className="market-card">
            <div className="market-header">
              <div className="market-title">
                <h3>{market.market_name}</h3>
                <span className="market-type">{market.market_type}</span>
                <span className={`market-status ${market.market_status.toLowerCase()}`}>
                  {market.market_status}
                </span>
              </div>
              <div className="market-meta">
                <div>Event: {market.event_name}</div>
                <div>Total Matched: £{market.total_matched.toFixed(2)}</div>
                <div>Runners: {market.number_of_runners}</div>
              </div>
            </div>

            <div className="market-details">
              <div className="detail-row">
                <label>Market ID:</label>
                <value>{market.market_id}</value>
              </div>
              <div className="detail-row">
                <label>Event ID:</label>
                <value>{market.event_id}</value>
              </div>
              {market.country_code && (
                <div className="detail-row">
                  <label>Country:</label>
                  <value>{market.country_code}</value>
                </div>
              )}
              <div className="detail-row">
                <label>In-Play:</label>
                <value>{market.inplay ? 'Yes' : 'No'}</value>
              </div>
            </div>

            <div className="runners-section">
              <h4>Runners</h4>
              {market.runners.map((runner, runnerIndex) => (
                <div key={runnerIndex} className="runner-card">
                  <div
                    className="runner-header"
                    onClick={() => toggleRunner(`${marketIndex}-${runnerIndex}`)}
                  >
                    <div className="runner-info">
                      <span className="runner-toggle">
                        {expandedRunners.has(`${marketIndex}-${runnerIndex}`) ? '▼' : '▶'}
                      </span>
                      <span className="runner-id">#{runner.selection_id}</span>
                      <span className="runner-name">{runner.runner_name}</span>
                      <span className={`runner-status ${runner.status.toLowerCase()}`}>
                        {runner.status}
                      </span>
                    </div>
                    <div className="runner-prices">
                      {runner.last_price_traded && (
                        <span>LPT: {runner.last_price_traded.toFixed(2)}</span>
                      )}
                    </div>
                  </div>

                  {expandedRunners.has(`${marketIndex}-${runnerIndex}`) && (
                    <div className="runner-details">
                      <div className="price-section">
                        <h5>BSP (Starting Price)</h5>
                        <div className="price-grid">
                          {runner.bsp.near_price && (
                            <div><label>Near:</label> <value>{runner.bsp.near_price}</value></div>
                          )}
                          {runner.bsp.far_price && (
                            <div><label>Far:</label> <value>{runner.bsp.far_price}</value></div>
                          )}
                          {runner.bsp.actual_sp && (
                            <div><label>Actual SP:</label> <value>{runner.bsp.actual_sp}</value></div>
                          )}
                        </div>
                      </div>

                      {runner.ex.available_to_back.length > 0 && (
                        <div className="price-section">
                          <h5>Available to Back</h5>
                          <div className="price-list">
                            {runner.ex.available_to_back.slice(0, 5).map((item, i) => (
                              <div key={i} className="price-item">
                                <span>{item[0]}</span>
                                <span>£{item[1].toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {runner.ex.available_to_lay.length > 0 && (
                        <div className="price-section">
                          <h5>Available to Lay</h5>
                          <div className="price-list">
                            {runner.ex.available_to_lay.slice(0, 5).map((item, i) => (
                              <div key={i} className="price-item">
                                <span>{item[0]}</span>
                                <span>£{item[1].toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="viewer-actions">
        <button className="btn btn-secondary" onClick={() => onExport(fileId, 'csv')}>
          Export as CSV
        </button>
        <button className="btn btn-secondary" onClick={() => onExport(fileId, 'json')}>
          Export as JSON
        </button>
        <button className="btn btn-danger" onClick={() => onDelete(fileId)}>
          Delete File
        </button>
      </div>
    </div>
  );
}

export default FileViewer;
