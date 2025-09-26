import React, { useState, useRef, useEffect } from 'react';
import { FiMic, FiMicOff, FiType, FiSend, FiVolume2 } from 'react-icons/fi';
import RecordRTC from 'recordrtc';
import './VoiceInput.css';

const VoiceInput = ({
  isRecording,
  isProcessing,
  onStartRecording,
  onStopRecording,
  onVoiceProcessed,
  onTextSubmit
}) => {
  const [textInput, setTextInput] = useState('');
  const [inputMode, setInputMode] = useState('voice'); // 'voice' or 'text'
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const animationFrameRef = useRef(null);
  const analyserRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Timer effect for recording
  useEffect(() => {
    if (isRecording) {
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setRecordingTime(0);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRecording]);

  const startRecording = async () => {
    try {
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;

      // Set up audio level monitoring
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = { analyser, audioContext };

      // Monitor audio levels
      const monitorAudioLevel = () => {
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255);
        
        if (isRecording) {
          animationFrameRef.current = requestAnimationFrame(monitorAudioLevel);
        }
      };
      
      monitorAudioLevel();

      // Set up RecordRTC
      mediaRecorderRef.current = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/webm',
        recorderType: RecordRTC.StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: 16000,
        bufferSize: 4096
      });

      mediaRecorderRef.current.startRecording();
      onStartRecording();

    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stopRecording(() => {
        const audioBlob = mediaRecorderRef.current.getBlob();
        onVoiceProcessed(audioBlob);
      });
    }

    // Clean up audio monitoring
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (analyserRef.current) {
      analyserRef.current.audioContext.close();
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    setAudioLevel(0);
    onStopRecording();
  };

  const handleVoiceClick = () => {
    if (isProcessing) return;
    
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleTextSubmit = (e) => {
    e.preventDefault();
    if (textInput.trim() && !isProcessing) {
      onTextSubmit(textInput.trim());
      setTextInput('');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAudioLevelClass = () => {
    if (audioLevel > 0.7) return 'high';
    if (audioLevel > 0.3) return 'medium';
    return 'low';
  };

  return (
    <div className="voice-input card">
      <div className="input-header">
        <h2>Voice Input</h2>
        <div className="input-mode-toggle">
          <button
            className={`mode-btn ${inputMode === 'voice' ? 'active' : ''}`}
            onClick={() => setInputMode('voice')}
          >
            <FiMic size={16} />
            Voice
          </button>
          <button
            className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
            onClick={() => setInputMode('text')}
          >
            <FiType size={16} />
            Text
          </button>
        </div>
      </div>

      {inputMode === 'voice' ? (
        <div className="voice-controls">
          {/* Microphone Button */}
          <div className="mic-container">
            <button
              className={`mic-button ${isRecording ? 'recording' : ''} ${isProcessing ? 'processing' : ''}`}
              onClick={handleVoiceClick}
              disabled={isProcessing}
            >
              <div className="mic-icon-container">
                {isRecording ? (
                  <FiMicOff size={32} />
                ) : (
                  <FiMic size={32} />
                )}
              </div>
              
              {/* Recording animation rings */}
              {isRecording && (
                <div className="recording-rings">
                  <div className="ring ring-1"></div>
                  <div className="ring ring-2"></div>
                  <div className="ring ring-3"></div>
                </div>
              )}
            </button>

            {/* Audio level indicator */}
            {isRecording && (
              <div className="audio-level-container">
                <div className={`audio-level ${getAudioLevelClass()}`}>
                  <div 
                    className="audio-level-bar"
                    style={{ height: `${audioLevel * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Recording Status */}
          <div className="recording-status">
            {isRecording && (
              <div className="recording-info">
                <div className="recording-indicator">
                  <div className="pulse-dot"></div>
                  Recording...
                </div>
                <div className="recording-time">
                  {formatTime(recordingTime)}
                </div>
              </div>
            )}
            
            {isProcessing && (
              <div className="processing-info">
                <div className="spinner-small"></div>
                Processing your voice...
              </div>
            )}

            {!isRecording && !isProcessing && (
              <div className="instruction-text">
                <FiVolume2 size={16} />
                Click the microphone to start speaking
              </div>
            )}
          </div>

          {/* Voice Tips */}
          <div className="voice-tips">
            <h4>💡 Voice Tips:</h4>
            <ul>
              <li>Speak clearly and describe what you want to see</li>
              <li>Include colors, objects, and settings</li>
              <li>Try: "Draw a sunny beach with palm trees"</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="text-controls">
          <form onSubmit={handleTextSubmit} className="text-form">
            <div className="text-input-container">
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Describe what you want to visualize... 
                
Example: 'A peaceful mountain lake at sunset with snow-capped peaks reflecting in the water'"
                className="text-input"
                rows={4}
                disabled={isProcessing}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={!textInput.trim() || isProcessing}
              >
                {isProcessing ? (
                  <div className="spinner-small"></div>
                ) : (
                  <FiSend size={20} />
                )}
                {isProcessing ? 'Processing...' : 'Generate'}
              </button>
            </div>
          </form>

          {/* Text Tips */}
          <div className="text-tips">
            <h4>✍️ Text Tips:</h4>
            <ul>
              <li>Be descriptive - include details about colors, style, mood</li>
              <li>Mention the setting or environment</li>
              <li>Specify art style: realistic, cartoon, sketch, painting</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceInput;