import React from 'react';

function ExportCenter({ files, onExport }) {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Export Center</h1>
      <p>Batch export files in various formats</p>
      <p>Files available: {files.length}</p>
      {/* TODO: Implement batch export functionality */}
    </div>
  );
}

export default ExportCenter;
