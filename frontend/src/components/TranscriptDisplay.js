import React from 'react';
import './TranscriptDisplay.css';

const TranscriptDisplay = ({ transcript, isProcessing, visualConcepts }) => {
  return (
    <div className="transcript-display card">
      <div className="transcript-header">
        <h3>Voice Transcript</h3>
        {isProcessing && <div className="processing-indicator">Processing...</div>}
      </div>
      
      <div className="transcript-content">
        {transcript ? (
          <div className="transcript-text">
            <p>"{transcript}"</p>
          </div>
        ) : (
          <div className="transcript-placeholder">
            <p>Your voice transcript will appear here...</p>
          </div>
        )}
      </div>

      {visualConcepts && (
        <div className="visual-concepts">
          <h4>Detected Concepts:</h4>
          <div className="concepts-list">
            {visualConcepts.keywords?.map((keyword, index) => (
              <span key={index} className="concept-tag">{keyword}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptDisplay;