import React, { useState } from 'react';
import { FiSettings, FiWifi, FiWifiOff, FiInfo } from 'react-icons/fi';
import './Header.css';

const Header = ({ connectionStatus, settings, onSettingsUpdate }) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showAbout, setShowAbout] = useState(false);

  const handleSettingsChange = (key, value) => {
    onSettingsUpdate({ [key]: value });
  };

  const getConnectionIcon = () => {
    return connectionStatus === 'connected' ? 
      <FiWifi className="connection-icon connected" /> : 
      <FiWifiOff className="connection-icon disconnected" />;
  };

  return (
    <>
      <header className="header glass">
        <div className="header-content">
          {/* Logo and Title */}
          <div className="logo-section">
            <div className="logo">
              <span className="logo-icon">🎨</span>
              <div className="logo-text">
                <h1>ECHOSKETCH</h1>
                <span className="tagline">Voice to Visuals</span>
              </div>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="status-section">
            <div className={`connection-status ${connectionStatus}`}>
              {getConnectionIcon()}
              <span className="status-text">
                {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          {/* Header Actions */}
          <div className="header-actions">
            <button
              className="header-btn"
              onClick={() => setShowAbout(true)}
              title="About ECHOSKETCH"
            >
              <FiInfo size={20} />
            </button>
            
            <button
              className="header-btn"
              onClick={() => setShowSettings(true)}
              title="Settings"
            >
              <FiSettings size={20} />
            </button>
          </div>
        </div>
      </header>

      {/* Settings Modal */}
      {showSettings && (
        <div className="modal-overlay" onClick={() => setShowSettings(false)}>
          <div className="modal glass" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Settings</h2>
              <button 
                className="modal-close"
                onClick={() => setShowSettings(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              {/* Image Style Setting */}
              <div className="setting-group">
                <label className="setting-label">Image Style</label>
                <select
                  value={settings.imageStyle}
                  onChange={(e) => handleSettingsChange('imageStyle', e.target.value)}
                  className="setting-select"
                >
                  <option value="illustration">Illustration</option>
                  <option value="realistic">Realistic</option>
                  <option value="cartoon">Cartoon</option>
                  <option value="sketch">Sketch</option>
                  <option value="painting">Painting</option>
                  <option value="digital art">Digital Art</option>
                </select>
              </div>

              {/* Image Size Setting */}
              <div className="setting-group">
                <label className="setting-label">Image Size</label>
                <select
                  value={settings.imageSize}
                  onChange={(e) => handleSettingsChange('imageSize', e.target.value)}
                  className="setting-select"
                >
                  <option value="256x256">256 × 256</option>
                  <option value="512x512">512 × 512</option>
                  <option value="1024x1024">1024 × 1024</option>
                </select>
              </div>

              {/* History Setting */}
              <div className="setting-group">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.enableHistory}
                    onChange={(e) => handleSettingsChange('enableHistory', e.target.checked)}
                    className="setting-checkbox"
                  />
                  Enable Session History
                </label>
              </div>

              {/* Auto Save Setting */}
              <div className="setting-group">
                <label className="setting-label">
                  <input
                    type="checkbox"
                    checked={settings.autoSave}
                    onChange={(e) => handleSettingsChange('autoSave', e.target.checked)}
                    className="setting-checkbox"
                  />
                  Auto-save Generated Images
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* About Modal */}
      {showAbout && (
        <div className="modal-overlay" onClick={() => setShowAbout(false)}>
          <div className="modal glass" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>About ECHOSKETCH</h2>
              <button 
                className="modal-close"
                onClick={() => setShowAbout(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="about-content">
                <p>
                  <strong>ECHOSKETCH - Voice to Visuals</strong> is an innovative multimodal AI system 
                  that converts speech into real-time visual representations.
                </p>
                
                <h3>Features:</h3>
                <ul>
                  <li>🎤 Voice-to-Visual conversion</li>
                  <li>🧠 Advanced speech recognition</li>
                  <li>🎨 AI-powered image generation</li>
                  <li>⚡ Real-time processing</li>
                  <li>♿ Accessibility-focused design</li>
                  <li>📱 Responsive interface</li>
                </ul>

                <h3>How to use:</h3>
                <ol>
                  <li>Click the microphone button to start recording</li>
                  <li>Describe what you want to visualize</li>
                  <li>Watch as your words become visuals!</li>
                </ol>

                <div className="version-info">
                  <small>Version 1.0.0 | Built with React & Flask</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Header;