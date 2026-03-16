import React from "react";
import { Link } from "react-router-dom";

function Layout({ children }) {
  return (
    <>
      {/* Navigation */}
      <nav className="navbar navbar-expand-lg navbar-dark fixed-top glass-nav">
        <div className="container-fluid px-4">

          <Link className="navbar-brand fw-bold" to="/">
            <i className="bi bi-house-heart-fill me-2 text-accent"></i>
            CohabitAI
          </Link>

          <button
            className="navbar-toggler border-0"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
          >
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto align-items-center gap-1">

              <li className="nav-item">
                <Link className="nav-link" to="/dashboard">
                  <i className="bi bi-speedometer2 me-1"></i>Dashboard
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/map">
                  <i className="bi bi-geo-alt me-1"></i>Map
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/search">
                  <i className="bi bi-search-heart me-1"></i>Search
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/compare">
                  <i className="bi bi-bar-chart-line me-1"></i>Compare
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/reviews">
                  <i className="bi bi-star me-1"></i>Reviews
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/chatbot">
                  <i className="bi bi-chat-dots me-1"></i>AI Chat
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/architecture">
                  <i className="bi bi-diagram-3 me-1"></i>Architecture
                </Link>
              </li>

              <li className="nav-item">
                <Link className="nav-link" to="/login">
                  <i className="bi bi-box-arrow-in-right me-1"></i>Login
                </Link>
              </li>

              <li className="nav-item">
                <Link className="btn btn-accent btn-sm px-3" to="/register">
                  <i className="bi bi-rocket-takeoff me-1"></i>Sign Up
                </Link>
              </li>

            </ul>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ marginTop: "80px" }}>
        {children}
      </main>

      {/* Footer */}
      <footer className="text-center py-4 mt-5 border-top border-secondary border-opacity-25">
        <div className="container">
          <p className="text-muted mb-1">
            © 2026 CohabitAI — AI-Driven Geo-Spatial Compatibility Platform
          </p>
          <small className="text-muted">
            Built for smarter shared living.
          </small>
        </div>
      </footer>
    </>
  );
}

export default Layout;