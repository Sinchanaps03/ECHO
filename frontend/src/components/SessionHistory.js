import React from 'react';
import { FiClock, FiImage } from 'react-icons/fi';
import './SessionHistory.css';

const SessionHistory = ({ sessions, currentSession, onSessionSelect }) => {
  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = now - then;
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`;
    return `${Math.floor(minutes / 1440)}d ago`;
  };

  return (
    <div className="session-history card">
      <div className="history-header">
        <h3>Recent Sessions</h3>
        <span className="session-count">{sessions.length}</span>
      </div>

      <div className="history-list">
        {sessions.length > 0 ? (
          sessions.map((session, index) => (
            <div 
              key={session.session_id || index}
              className={`history-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
              onClick={() => onSessionSelect(session)}
            >
              <div className="item-content">
                <div className="item-text">
                  <p className="transcript-preview">
                    {session.transcript?.substring(0, 50)}
                    {session.transcript?.length > 50 ? '...' : ''}
                  </p>
                  <div className="item-meta">
                    <FiClock size={12} />
                    <span>{formatTimeAgo(session.timestamp)}</span>
                    {session.image_data && (
                      <>
                        <FiImage size={12} />
                        <span>{session.image_data.generator}</span>
                      </>
                    )}
                  </div>
                </div>
                {session.image_data?.image_url && (
                  <div className="item-thumbnail">
                    <img 
                      src={session.image_data.image_url} 
                      alt="Generated"
                    />
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="empty-history">
            <p>No sessions yet</p>
            <small>Your voice-to-visual sessions will appear here</small>
          </div>
        )}
      </div>
    </div>
  );
};

export default SessionHistory;