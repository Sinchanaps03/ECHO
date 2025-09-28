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
        
        # Initialize SpeechRecognition as fallback
        self.sr_recognizer = None
        try:
            import speech_recognition as sr
            self.sr_recognizer = sr.Recognizer()
            logger.info("SpeechRecognition library initialized as fallback")
        except ImportError:
            logger.warning("SpeechRecognition library not available")
    
    def speech_to_text(self, audio_file_path):
        """
        Convert audio file to text using available speech recognition services
        """
        try:
            # First try with Google Cloud Speech API if available
            if self.google_client:
                return self._google_speech_to_text(audio_file_path)
            # Then try with SpeechRecognition library
            elif self.sr_recognizer:
                return self._speechrecognition_to_text(audio_file_path)
            else:
                # For demo purposes, return a placeholder response
                logger.warning("No speech recognition service available. Using placeholder.")
                return "This is a placeholder transcript. Please configure speech recognition services."
                
        except Exception as e:
            logger.error(f"Error in speech to text conversion: {e}")
            # Try fallback if primary method fails
            if self.sr_recognizer and not self.google_client:
                try:
                    return self._speechrecognition_to_text(audio_file_path)
                except:
                    pass
            return None
    
    def _speechrecognition_to_text(self, audio_file_path):
        """
        Use SpeechRecognition library for transcription
        """
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
            logger.info("Converting audio with SpeechRecognition library...")
            
            # Convert WebM to WAV for SpeechRecognition
            audio = AudioSegment.from_file(audio_file_path)
            wav_path = audio_file_path.replace('.webm', '.wav')
            audio.export(wav_path, format="wav")
            
            # Use SpeechRecognition
            with sr.AudioFile(wav_path) as source:
                audio_data = self.sr_recognizer.record(source)
                text = self.sr_recognizer.recognize_google(audio_data)
                
            # Clean up temporary WAV file
            if os.path.exists(wav_path):
                os.remove(wav_path)
                
            logger.info(f"SpeechRecognition transcription successful: {text[:50]}...")
            return text
            
        except Exception as e:
            logger.error(f"Error in SpeechRecognition transcription: {e}")
            raise e
    
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