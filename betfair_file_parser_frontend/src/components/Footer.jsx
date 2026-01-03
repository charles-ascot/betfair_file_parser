import React from 'react';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div>&copy; {currentYear} Ascot Wealth Management. All rights reserved.</div>
        <div className="footer-section">
          <a href="#privacy">Privacy</a>
          <span>•</span>
          <a href="#terms">Terms</a>
          <span>•</span>
          <span>v1.0.0</span>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
