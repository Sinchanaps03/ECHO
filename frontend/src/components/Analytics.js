import React, { useState, useEffect } from 'react';
import './Analytics.css';

const Analytics = ({ isOpen, onClose }) => {
  const [metrics, setMetrics] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [activeChart, setActiveChart] = useState('accuracy');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchAnalytics();
    }
  }, [isOpen]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchChartData = async (chartType) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/performance-chart?type=${chartType}`);
      const data = await response.json();
      setChartData(data);
      setActiveChart(chartType);
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const renderSimpleChart = () => {
    if (!chartData) return <div className="loading">Select a chart to view</div>;
    if (loading) return <div className="loading">Loading chart...</div>;

    const { chartType, data, title } = chartData;

    if (chartType === 'line') {
      return (
        <div className="simple-line-chart">
          <h4>{title}</h4>
          <div className="chart-container">
            <svg width="400" height="200" viewBox="0 0 400 200">
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#4ECDC4" />
                  <stop offset="100%" stopColor="#44A08D" />
                </linearGradient>
              </defs>
              {data.map((point, index) => {
                const x = (index / (data.length - 1)) * 380 + 10;
                const y = 180 - (point.value / 100) * 160;
                const nextPoint = data[index + 1];
                
                return (
                  <g key={index}>
                    <circle cx={x} cy={y} r="4" fill="url(#lineGradient)" />
                    {nextPoint && (
                      <line 
                        x1={x} 
                        y1={y} 
                        x2={((index + 1) / (data.length - 1)) * 380 + 10} 
                        y2={180 - (nextPoint.value / 100) * 160}
                        stroke="url(#lineGradient)" 
                        strokeWidth="2"
                      />
                    )}
                    <text x={x} y={195} textAnchor="middle" fontSize="10" fill="#666">
                      {point.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
        </div>
      );
    }

    if (chartType === 'bar') {
      const maxValue = Math.max(...data.map(item => item.value));
      const colors = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFA07A'];
      
      return (
        <div className="simple-bar-chart">
          <h4>{title}</h4>
          <div className="bars">
            {data.map((item, index) => (
              <div key={index} className="bar-item">
                <div 
                  className="bar" 
                  style={{ 
                    height: `${(item.value / maxValue) * 150}px`,
                    backgroundColor: colors[index % colors.length]
                  }}
                >
                  <span className="bar-value">{item.value}</span>
                </div>
                <span className="bar-label">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (chartType === 'doughnut') {
      const total = data.reduce((sum, item) => sum + item.value, 0);
      const colors = ['#4ECDC4', '#FF6B6B', '#45B7D1', '#96CEB4', '#FFA07A'];
      
      return (
        <div className="simple-doughnut-chart">
          <h4>{title}</h4>
          <div className="chart-container">
            <svg width="200" height="200" viewBox="0 0 200 200">
              <circle cx="100" cy="100" r="80" fill="none" stroke="#f0f0f0" strokeWidth="20"/>
              {data.map((item, index) => {
                const percentage = (item.value / total) * 100;
                const angle = (percentage / 100) * 360;
                const startAngle = data.slice(0, index).reduce((sum, prev) => 
                  sum + (prev.value / total) * 360, 0);
                
                const x1 = 100 + 80 * Math.cos((startAngle - 90) * Math.PI / 180);
                const y1 = 100 + 80 * Math.sin((startAngle - 90) * Math.PI / 180);
                const x2 = 100 + 80 * Math.cos((startAngle + angle - 90) * Math.PI / 180);
                const y2 = 100 + 80 * Math.sin((startAngle + angle - 90) * Math.PI / 180);
                
                const largeArc = angle > 180 ? 1 : 0;
                
                return (
                  <path
                    key={index}
                    d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                    fill={colors[index % colors.length]}
                  />
                );
              })}
              <circle cx="100" cy="100" r="40" fill="white"/>
            </svg>
          </div>
          <div className="doughnut-legend">
            {data.map((item, index) => (
              <div key={index} className="legend-item">
                <div 
                  className="legend-color" 
                  style={{ backgroundColor: colors[index % colors.length] }}
                />
                <span>{item.label}: {item.value}</span>
              </div>
            ))}
          </div>
        </div>
      );
    }

    return <div className="loading">Unsupported chart type</div>;
  };

  return (
    <div className="analytics-overlay">
      <div className="analytics-modal">
        <div className="analytics-header">
          <h2>Performance Analytics</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="analytics-content">
          {metrics && (
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{metrics.totalSessions || 0}</div>
                <div className="metric-label">Total Sessions</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{metrics.averageAccuracy || 0}%</div>
                <div className="metric-label">Average Accuracy</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{metrics.averageResponseTime || 0}ms</div>
                <div className="metric-label">Avg Response Time</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{metrics.totalConcepts || 0}</div>
                <div className="metric-label">Concepts Detected</div>
              </div>
            </div>
          )}

          <div className="chart-controls">
            <h3>Performance Charts</h3>
            <div className="chart-buttons">
              <button 
                className={`chart-button ${activeChart === 'accuracy' ? 'active' : ''}`}
                onClick={() => fetchChartData('accuracy')}
                disabled={loading}
              >
                Accuracy Trends
              </button>
              <button 
                className={`chart-button ${activeChart === 'objects' ? 'active' : ''}`}
                onClick={() => fetchChartData('objects')}
                disabled={loading}
              >
                Popular Objects
              </button>
              <button 
                className={`chart-button ${activeChart === 'colors' ? 'active' : ''}`}
                onClick={() => fetchChartData('colors')}
                disabled={loading}
              >
                Color Distribution
              </button>
              <button 
                className={`chart-button ${activeChart === 'response-times' ? 'active' : ''}`}
                onClick={() => fetchChartData('response-times')}
                disabled={loading}
              >
                Response Times
              </button>
            </div>
          </div>

          <div className="chart-display">
            {renderSimpleChart()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;