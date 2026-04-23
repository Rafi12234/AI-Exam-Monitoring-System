import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../styles/Navigation.css';

export default function Navigation() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <Link to="/" className="logo-link">
            🎓 Exam Monitor
          </Link>
        </div>

        <div className="nav-menu">
          <Link
            to="/"
            className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}
          >
            <span className="icon">📊</span>
            <span className="label">Dashboard</span>
          </Link>

          <Link
            to="/camera"
            className={`nav-item ${location.pathname === '/camera' ? 'active' : ''}`}
          >
            <span className="icon">📹</span>
            <span className="label">Camera Monitor</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}
