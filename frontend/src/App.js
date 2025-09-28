import React, { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Import components
import Header from './components/Header';
import VoiceInput from './components/VoiceInput';
import TranscriptDisplay from './components/TranscriptDisplay';
import ImageDisplay from './components/ImageDisplay';
import ControlPanel from './components/ControlPanel';
import SessionHistory from './components/SessionHistory';
import LoadingSpinner from './components/LoadingSpinner';
import Analytics from './components/Analytics';

// Import services
import SocketService from './services/SocketService';
import ApiService from './services/ApiService';

// Import styles
import './App.css';

function App() {
  // State management
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [generatedImage, setGeneratedImage] = useState(null);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [settings, setSettings] = useState({
    imageStyle: 'illustration',
    imageSize: '512x512',
    enableHistory: true,
    autoSave: true
  });

  // Initialize socket connection on component mount
  useEffect(() => {
    // Initialize socket connection
    SocketService.connect();
    
    // Set up socket event listeners
    SocketService.on('connected', (data) => {
      setConnectionStatus('connected');
      toast.success('Connected to ECHOSKETCH!');
    });

    SocketService.on('processing', (data) => {
      toast.info('Processing your voice...');
    });

    SocketService.on('error', (data) => {
      toast.error(`Error: ${data.message}`);
      setIsProcessing(false);
    });

    // Load session history
    loadSessionHistory();

    // Cleanup on component unmount
    return () => {
      SocketService.disconnect();
    };
  }, []);

  // Load session history from API
  const loadSessionHistory = async () => {
    try {
      // This would be implemented when we have a sessions endpoint
      // const history = await ApiService.getRecentSessions();
      // setSessionHistory(history);
    } catch (error) {
      console.error('Error loading session history:', error);
    }
  };

  // Handle voice recording start
  const handleStartRecording = () => {
    if (!isProcessing) {
      setIsRecording(true);
      setTranscript('');
      setGeneratedImage(null);
      toast.info('Listening... Start speaking!');
    }
  };

  // Handle voice recording stop
  const handleStopRecording = () => {
    setIsRecording(false);
    toast.info('Processing your voice...');
  };

  // Handle voice processing completion
  const handleVoiceProcessed = async (audioBlob) => {
    if (!audioBlob) {
      toast.error('No audio recorded');
      return;
    }

    setIsProcessing(true);
    
    try {
      // Create FormData to send audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      // Send to backend for processing
      const response = await ApiService.processVoice(formData);

      if (response.success) {
        setTranscript(response.transcript);
        setGeneratedImage(response.image_data);
        setCurrentSession(response);

        // Add to session history if enabled
        if (settings.enableHistory) {
          setSessionHistory(prev => [response, ...prev.slice(0, 9)]);
        }

        toast.success('Image generated successfully!');
      } else {
        toast.error('Failed to process voice');
      }

    } catch (error) {
      console.error('Error processing voice:', error);
      toast.error('Error processing voice. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle text input submission
  const handleTextSubmit = async (text) => {
    console.log('handleTextSubmit called with text:', text);
    
    if (!text.trim()) {
      toast.warning('Please enter some text');
      return;
    }

    console.log('Starting API request...');
    setIsProcessing(true);
    setTranscript(text);
    setGeneratedImage(null);

    try {
      console.log('Calling ApiService.textToImage with:', { text });
      const response = await ApiService.textToImage({ text });
      console.log('API response received:', response);

      if (response.success) {
        console.log('Success response, setting generated image:', response.image_data);
        setTranscript(response.transcript);
        setGeneratedImage(response.image_data);
        setCurrentSession(response);

        // Add to session history
        if (settings.enableHistory) {
          setSessionHistory(prev => [response, ...prev.slice(0, 9)]);
        }

        toast.success('Image generated successfully!');
      } else {
        toast.error('Failed to generate image');
      }

    } catch (error) {
      console.error('Error generating image:', error);
      toast.error('Error generating image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle session selection from history
  const handleSessionSelect = (session) => {
    setCurrentSession(session);
    setTranscript(session.transcript);
    setGeneratedImage(session.image_data);
    toast.info('Session loaded');
  };

  // Handle settings update
  const handleSettingsUpdate = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    toast.success('Settings updated');
  };

  // Clear current session
  const handleClearSession = () => {
    setCurrentSession(null);
    setTranscript('');
    setGeneratedImage(null);
    setIsRecording(false);
    setIsProcessing(false);
    toast.info('Session cleared');
  };

  return (
    <div className="app">
      {/* Header */}
      <Header 
        connectionStatus={connectionStatus}
        settings={settings}
        onSettingsUpdate={handleSettingsUpdate}
      />

      {/* Main Content */}
      <main className="main-content">
        <div className="content-grid">
          
          {/* Left Column - Voice Input & Controls */}
          <div className="left-column">
            <VoiceInput
              isRecording={isRecording}
              isProcessing={isProcessing}
              onStartRecording={handleStartRecording}
              onStopRecording={handleStopRecording}
              onVoiceProcessed={handleVoiceProcessed}
              onTextSubmit={handleTextSubmit}
            />

            <ControlPanel
              currentSession={currentSession}
              settings={settings}
              onSettingsUpdate={handleSettingsUpdate}
              onClearSession={handleClearSession}
              onShowAnalytics={() => setShowAnalytics(true)}
            />
          </div>

          {/* Middle Column - Transcript & Image */}
          <div className="middle-column">
            {/* Transcript Display */}
            <TranscriptDisplay
              transcript={transcript}
              isProcessing={isProcessing}
              visualConcepts={currentSession?.visual_concepts}
            />

            {/* Image Display */}
            <ImageDisplay
              imageData={generatedImage}
              isGenerating={isProcessing && !generatedImage}
              onImageSave={() => toast.success('Image saved!')}
              onImageExport={() => toast.success('Image exported!')}
            />

            {/* Processing Indicator */}
            {isProcessing && (
              <div className="processing-indicator">
                <LoadingSpinner />
                <p>Processing your request...</p>
              </div>
            )}
          </div>

          {/* Right Column - Session History */}
          <div className="right-column">
            {settings.enableHistory && (
              <SessionHistory
                sessions={sessionHistory}
                currentSession={currentSession}
                onSessionSelect={handleSessionSelect}
              />
            )}
          </div>

        </div>
      </main>

      {/* Toast Notifications */}
      <ToastContainer
        position="bottom-right"
        autoClose={4000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        className="toast-container"
      />

      {/* Global Loading Overlay */}
      {isProcessing && (
        <div className="loading-overlay">
          <div className="loading-content glass">
            <LoadingSpinner large />
            <h3>Creating your visual...</h3>
            <p>This may take a few moments</p>
          </div>
        </div>
      )}

      {/* Analytics Modal */}
      <Analytics 
        isOpen={showAnalytics}
        onClose={() => setShowAnalytics(false)}
      />
    </div>
  );
}

export default App;