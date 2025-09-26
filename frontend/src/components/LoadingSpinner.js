import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ large = false, message = '' }) => {
  return (
    <div className={`loading-spinner-container ${large ? 'large' : ''}`}>
      <div className={`spinner ${large ? 'spinner-large' : 'spinner-small'}`}>
        <div className="spinner-inner">
          <div className="spinner-circle"></div>
          <div className="spinner-circle"></div>
          <div className="spinner-circle"></div>
        </div>
      </div>
      {message && <p className="spinner-message">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;