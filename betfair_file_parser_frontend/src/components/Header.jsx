import React from 'react';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">⚡</div>
          <div>
            <div>Betfair File Parser</div>
            <div className="header-subtitle">Powered by IntakeHub v3.0.0</div>
          </div>
        </div>
        <div className="status-indicator">
          <div className="status-dot"></div>
          <span>API Connected</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
