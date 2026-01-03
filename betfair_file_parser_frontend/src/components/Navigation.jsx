import React from 'react';

function Navigation({ currentPage, onPageChange }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'upload', label: 'Upload Files', icon: '📤' },
    { id: 'viewer', label: 'File Viewer', icon: '👁️' },
    { id: 'browser', label: 'Market Browser', icon: '🔍' },
    { id: 'export', label: 'Export Center', icon: '💾' },
  ];

  return (
    <nav className="navigation">
      <div className="nav-section">
        <div className="nav-section-title">Main</div>
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => onPageChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}

export default Navigation;
