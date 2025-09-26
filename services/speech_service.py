import os
import logging
import io

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        # Initialize Google Cloud Speech client if credentials are available
        self.google_client = None
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            try:
                from google.cloud import speech
                self.google_client = speech.SpeechClient()
                logger.info("Google Cloud Speech client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Google Cloud Speech: {e}")
    
    def speech_to_text(self, audio_file_path):
        """
        Convert audio file to text using available speech recognition services
        """
        try:
            # First try with Google Cloud Speech API if available
            if self.google_client:
                return self._google_speech_to_text(audio_file_path)
            else:
                # For demo purposes, return a placeholder response
                logger.warning("No speech recognition service available. Using placeholder.")
                return "This is a placeholder transcript. Please configure speech recognition services."
                
        except Exception as e:
            logger.error(f"Error in speech to text conversion: {e}")
            return None
    
    def _google_speech_to_text(self, audio_file_path):
        """
        Use Google Cloud Speech API for transcription
        """
        try:
            from google.cloud import speech
            
            with io.open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                model="latest_long",
            )
            
            response = self.google_client.recognize(config=config, audio=audio)
            
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                logger.info(f"Google Speech API transcript: {transcript} (confidence: {confidence})")
                return transcript
            else:
                logger.warning("No speech detected by Google Cloud Speech")
                return None
                
        except Exception as e:
            logger.error(f"Google Cloud Speech error: {e}")
            return None
    
    def listen_continuously(self, callback):
        """
        Listen continuously for speech input (placeholder implementation)
        """
        logger.warning("Continuous listening not available without speech recognition library")
        return None
    
    def is_microphone_available(self):
        """
        Check if microphone is available (placeholder implementation)
        """
        return True  # Assume available for demo purposes