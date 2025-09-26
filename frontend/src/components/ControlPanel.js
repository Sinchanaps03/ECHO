import React from 'react';
import { FiTrash2, FiSettings, FiRefreshCw } from 'react-icons/fi';
import './ControlPanel.css';

const ControlPanel = ({ currentSession, settings, onSettingsUpdate, onClearSession }) => {
  return (
    <div className="control-panel card">
      <div className="panel-header">
        <h3>Controls</h3>
      </div>

      <div className="panel-content">
        <div className="control-group">
          <h4>Session</h4>
          <div className="control-buttons">
            <button 
              className="control-btn danger"
              onClick={onClearSession}
              disabled={!currentSession}
            >
              <FiTrash2 size={16} />
              Clear Session
            </button>
          </div>
        </div>

        <div className="control-group">
          <h4>Quick Settings</h4>
          <div className="quick-settings">
            <div className="setting-item">
              <label>Image Style:</label>
              <select 
                value={settings.imageStyle}
                onChange={(e) => onSettingsUpdate({ imageStyle: e.target.value })}
              >
                <option value="illustration">Illustration</option>
                <option value="realistic">Realistic</option>
                <option value="cartoon">Cartoon</option>
                <option value="sketch">Sketch</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;