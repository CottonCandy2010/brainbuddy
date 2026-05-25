"""
Gemini Text-to-Speech Integration for Brain Buddy
Uses Google Cloud Text-to-Speech API with Gemini AI
"""

import os
import json
import base64
import requests
from io import BytesIO

class GeminiTTSService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        
    def generate_speech_audio(self, text, voice_gender='female', language_code='en-US'):
        """
        Generate speech audio using Google Cloud Text-to-Speech API
        """
        if not self.api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables")
        
        # Configure voice based on gender preference
        voice_name = self._get_voice_name(voice_gender, language_code)
        
        # Prepare the request payload
        payload = {
            "input": {
                "text": text
            },
            "voice": {
                "languageCode": language_code,
                "name": voice_name,
                "ssmlGender": "FEMALE" if voice_gender == 'female' else "MALE"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 0.8,
                "pitch": 0.0,
                "volumeGainDb": 0.0
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }
        
        try:
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                audio_content = result.get('audioContent')
                
                if audio_content:
                    # Decode base64 audio content
                    audio_data = base64.b64decode(audio_content)
                    return audio_data
                else:
                    raise Exception("No audio content in response")
            else:
                error_detail = response.text
                raise Exception(f"TTS API error {response.status_code}: {error_detail}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def _get_voice_name(self, voice_gender, language_code):
        """
        Get appropriate voice name based on gender and language
        """
        voice_map = {
            'en-US': {
                'female': 'en-US-Wavenet-F',
                'male': 'en-US-Wavenet-D'
            },
            'en-GB': {
                'female': 'en-GB-Wavenet-A',
                'male': 'en-GB-Wavenet-B'
            }
        }
        
        return voice_map.get(language_code, {}).get(voice_gender, 'en-US-Wavenet-F')
    
    def create_audio_url(self, text, voice_gender='female'):
        """
        Create a data URL for audio that can be played in the browser
        """
        try:
            audio_data = self.generate_speech_audio(text, voice_gender)
            
            # Convert to base64 for data URL
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            data_url = f"data:audio/mp3;base64,{audio_b64}"
            
            return data_url
        except Exception as e:
            print(f"Error creating audio URL: {str(e)}")
            return None