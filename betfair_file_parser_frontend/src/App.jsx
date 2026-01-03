import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import FileUpload from './pages/FileUpload';
import FileViewer from './pages/FileViewer';
import MarketBrowser from './pages/MarketBrowser';
import ExportCenter from './pages/ExportCenter';
import Footer from './components/Footer';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

  // Load files on mount
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiBaseUrl}/api/files`);
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
        setError(null);
      } else {
        setError('Failed to load files');
      }
    } catch (err) {
      console.error('Error loading files:', err);
      setError('Failed to connect to API');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (uploadedFiles) => {
    for (const file of uploadedFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${apiBaseUrl}/api/files/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          // Reload files list
          await loadFiles();
          setError(null);
        } else {
          const errorData = await response.json();
          setError(`Upload failed: ${errorData.detail || 'Unknown error'}`);
        }
      } catch (err) {
        console.error('Upload error:', err);
        setError('Failed to upload file');
      }
    }
  };

  const handleViewFile = (fileId) => {
    setSelectedFile(fileId);
    setCurrentPage('viewer');
  };

  const handleDeleteFile = async (fileId) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      try {
        const response = await fetch(`${apiBaseUrl}/api/files/${fileId}`, {
          method: 'DELETE',
        });
        
        if (response.ok) {
          await loadFiles();
          setError(null);
        } else {
          setError('Failed to delete file');
        }
      } catch (err) {
        console.error('Delete error:', err);
        setError('Failed to delete file');
      }
    }
  };

  const handleExport = async (fileId, format) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/files/${fileId}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format: format,
          include_prices: true,
        }),
      });

      if (response.ok) {
        // Create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `export.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        setError(null);
      } else {
        setError('Export failed');
      }
    } catch (err) {
      console.error('Export error:', err);
      setError('Failed to export file');
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard files={files} onViewFile={handleViewFile} />;
      case 'upload':
        return <FileUpload onFileUpload={handleFileUpload} loading={loading} />;
      case 'viewer':
        return (
          <FileViewer 
            fileId={selectedFile} 
            apiBaseUrl={apiBaseUrl}
            onDelete={handleDeleteFile}
            onExport={handleExport}
          />
        );
      case 'browser':
        return <MarketBrowser files={files} apiBaseUrl={apiBaseUrl} />;
      case 'export':
        return <ExportCenter files={files} onExport={handleExport} />;
      default:
        return <Dashboard files={files} onViewFile={handleViewFile} />;
    }
  };

  return (
    <div className="app">
      <Header />
      <div className="app-container">
        <Navigation currentPage={currentPage} onPageChange={setCurrentPage} />
        <main className="main-content">
          {error && (
            <div className="error-banner">
              <p>{error}</p>
              <button onClick={() => setError(null)}>×</button>
            </div>
          )}
          {renderPage()}
        </main>
      </div>
      <Footer />
    </div>
  );
}

export default App;
