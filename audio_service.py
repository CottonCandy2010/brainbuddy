try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

import os
import tempfile
from flask import send_file
import threading
import time

class AudioService:
    def __init__(self):
        self.engine = None
        self.init_engine()
    
    def init_engine(self):
        """Initialize the text-to-speech engine"""
        if not PYTTSX3_AVAILABLE:
            print("pyttsx3 not installed — TTS unavailable")
            return
        try:
            self.engine = pyttsx3.init()
            self.setup_default_settings()
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
    
    def setup_default_settings(self):
        """Setup default voice and speech settings"""
        if self.engine:
            # Set default rate and volume
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
    
    def get_available_voices(self):
        """Get list of available voices"""
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for i, voice in enumerate(voices):
            # Determine gender based on voice name/id
            gender = self.detect_voice_gender(voice.name if voice.name else voice.id)
            voice_info = {
                'id': i,
                'name': voice.name if voice.name else f"Voice {i+1}",
                'gender': gender,
                'language': getattr(voice, 'languages', ['en'])
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def detect_voice_gender(self, voice_name):
        """Detect voice gender based on name patterns"""
        voice_name_lower = voice_name.lower()
        
        # Common patterns for female voices
        female_indicators = ['female', 'woman', 'lady', 'girl', 'zira', 'helena', 'susan', 'anna', 'maria']
        
        # Common patterns for male voices
        male_indicators = ['male', 'man', 'boy', 'david', 'mark', 'james', 'george', 'alex']
        
        for indicator in female_indicators:
            if indicator in voice_name_lower:
                return 'female'
        
        for indicator in male_indicators:
            if indicator in voice_name_lower:
                return 'male'
        
        # Default to neutral if can't determine
        return 'neutral'
    
    def generate_speech_file(self, text, voice_id=None, rate=150, volume=0.8):
        """Generate speech audio file from text"""
        if not self.engine:
            return None
        
        try:
            # Set voice if specified
            if voice_id is not None:
                voices = self.engine.getProperty('voices')
                if 0 <= voice_id < len(voices):
                    self.engine.setProperty('voice', voices[voice_id].id)
            
            # Set speech rate and volume
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_filename = temp_file.name
            
            # Save speech to file
            self.engine.save_to_file(text, temp_filename)
            self.engine.runAndWait()
            
            return temp_filename
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def clean_text_for_speech(self, html_text):
        """Clean HTML text for better speech synthesis"""
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        
        # Replace common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', 'and')
        text = text.replace('&lt;', 'less than')
        text = text.replace('&gt;', 'greater than')
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Add pauses for better speech flow
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace(';', '; ')
        text = text.replace(':', ': ')
        
        return text

# Global audio service instance
audio_service = AudioService()