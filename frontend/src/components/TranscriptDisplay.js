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
          <div className="concepts-container">
            {visualConcepts.objects && visualConcepts.objects.length > 0 && (
              <div className="concept-category">
                <strong>Objects:</strong>
                <div className="concepts-list">
                  {visualConcepts.objects.map((obj, index) => (
                    <span key={index} className="concept-tag objects">{obj}</span>
                  ))}
                </div>
              </div>
            )}
            {visualConcepts.colors && visualConcepts.colors.length > 0 && (
              <div className="concept-category">
                <strong>Colors:</strong>
                <div className="concepts-list">
                  {visualConcepts.colors.map((color, index) => (
                    <span key={index} className="concept-tag colors">{color}</span>
                  ))}
                </div>
              </div>
            )}
            {visualConcepts.settings && visualConcepts.settings.length > 0 && (
              <div className="concept-category">
                <strong>Settings:</strong>
                <div className="concepts-list">
                  {visualConcepts.settings.map((setting, index) => (
                    <span key={index} className="concept-tag settings">{setting}</span>
                  ))}
                </div>
              </div>
            )}
            {(visualConcepts.mood || visualConcepts.style || visualConcepts.sentiment) && (
              <div className="concept-category">
                <strong>Attributes:</strong>
                <div className="concepts-list">
                  {visualConcepts.mood && <span className="concept-tag mood">Mood: {visualConcepts.mood}</span>}
                  {visualConcepts.style && <span className="concept-tag style">Style: {visualConcepts.style}</span>}
                  {visualConcepts.sentiment && <span className="concept-tag sentiment">Sentiment: {visualConcepts.sentiment}</span>}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptDisplay;