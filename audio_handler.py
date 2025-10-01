"""
Audio Handler Module
High-quality voice processing with Edge TTS and Faster-Whisper
NO PIPER - only natural-sounding voices
"""

import asyncio
import tempfile
import os
from config import config

class VoiceHandler:
    """Handles speech-to-text and text-to-speech with high quality"""
    
    def __init__(self):
        self.tts_engine = config.TTS_ENGINE
        self.stt_engine = config.STT_ENGINE
        self.whisper_model = None
        self.recognizer = None
        
        print(f"🎤 Audio Handler initialized")
        print(f"   TTS Engine: {self.tts_engine}")
        print(f"   STT Engine: {self.stt_engine}")
    
    def speech_to_text(self, audio_file_path):
        """Convert speech to text using configured engine"""
        if self.stt_engine == "faster-whisper":
            return self._whisper_transcribe(audio_file_path)
        elif self.stt_engine == "google":
            return self._google_transcribe(audio_file_path)
        else:
            return "⚠ Unknown STT engine configured"
    
    def _whisper_transcribe(self, audio_file_path):
        """Transcribe using Faster-Whisper (accurate, GPU-accelerated)"""
        try:
            # Lazy load Whisper model
            if self.whisper_model is None:
                print(f"Loading Whisper model: {config.WHISPER_MODEL_SIZE}")
                from faster_whisper import WhisperModel
                
                self.whisper_model = WhisperModel(
                    config.WHISPER_MODEL_SIZE,
                    device=config.WHISPER_DEVICE,
                    compute_type=config.WHISPER_COMPUTE_TYPE
                )
                print("✓ Whisper model loaded")
            
            # Transcribe
            segments, info = self.whisper_model.transcribe(
                audio_file_path,
                language="en",
                beam_size=5
            )
            
            # Combine segments
            transcription = " ".join([segment.text for segment in segments])
            
            print(f"✓ Transcribed: {transcription[:50]}...")
            return transcription.strip()
            
        except ImportError:
            print("⚠ faster-whisper not installed, falling back to Google")
            return self._google_transcribe(audio_file_path)
        except Exception as e:
            return f"⚠ Transcription error: {str(e)}"
    
    def _google_transcribe(self, audio_file_path):
        """Transcribe using Google Speech Recognition (fallback)"""
        try:
            import speech_recognition as sr
            
            if self.recognizer is None:
                self.recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                
            print(f"✓ Transcribed: {text[:50]}...")
            return text
            
        except Exception as e:
            return f"⚠ Transcription error: {str(e)}"
    
    def text_to_speech(self, text):
        """Convert text to speech using configured engine"""
        if self.tts_engine == "edge":
            return self._edge_tts(text)
        elif self.tts_engine == "coqui":
            return self._coqui_tts(text)
        elif self.tts_engine == "gtts":
            return self._gtts(text)
        else:
            return "⚠ Unknown TTS engine configured"
    
    def _edge_tts(self, text):
        """
        Generate speech using Edge TTS (Microsoft Azure voices)
        HIGH QUALITY - sounds natural, not robotic!
        """
        try:
            import edge_tts
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
            
            # Generate speech asynchronously
            async def generate():
                communicate = edge_tts.Communicate(
                    text,
                    voice=config.EDGE_VOICE,
                    rate=config.EDGE_RATE,
                    volume=config.EDGE_VOLUME
                )
                await communicate.save(output_path)
            
            # Run async function
            asyncio.run(generate())
            
            print(f"✓ Generated speech with Edge TTS ({config.EDGE_VOICE})")
            return output_path
            
        except ImportError:
            print("⚠ edge-tts not installed, install with: pip install edge-tts")
            return self._gtts(text)  # Fallback
        except Exception as e:
            print(f"⚠ Edge TTS error: {e}")
            return self._gtts(text)  # Fallback
    
    def _coqui_tts(self, text):
        """
        Generate speech using Coqui TTS (very high quality, slower)
        Optional high-end option
        """
        try:
            from TTS.api import TTS
            
            # Lazy load Coqui TTS
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            output_path = temp_file.name
            temp_file.close()
            
            # Generate
            tts.tts_to_file(text=text, file_path=output_path)
            
            print(f"✓ Generated speech with Coqui TTS")
            return output_path
            
        except ImportError:
            print("⚠ Coqui TTS not installed, falling back to Edge TTS")
            return self._edge_tts(text)
        except Exception as e:
            print(f"⚠ Coqui TTS error: {e}")
            return self._edge_tts(text)
    
    def _gtts(self, text):
        """
        Generate speech using gTTS (Google Text-to-Speech)
        Last resort fallback - acceptable quality
        """
        try:
            from gtts import gTTS
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            output_path = temp_file.name
            temp_file.close()
            
            # Generate
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_path)
            
            print(f"✓ Generated speech with gTTS (fallback)")
            return output_path
            
        except Exception as e:
            print(f"⚠ gTTS error: {e}")
            return None
    
    def list_available_voices(self):
        """List available Edge TTS voices"""
        if self.tts_engine != "edge":
            return ["Voice listing only available for Edge TTS"]
        
        try:
            import edge_tts
            
            async def get_voices():
                voices = await edge_tts.list_voices()
                return voices
            
            voices = asyncio.run(get_voices())
            
            # Filter to English voices and format
            english_voices = [
                {
                    "name": v["ShortName"],
                    "gender": v["Gender"],
                    "locale": v["Locale"]
                }
                for v in voices if v["Locale"].startswith("en-")
            ]
            
            return english_voices
            
        except Exception as e:
            print(f"⚠ Error listing voices: {e}")
            return []
    
    def change_voice(self, voice_name):
        """Change the active TTS voice (Edge TTS only)"""
        if self.tts_engine != "edge":
            return False
        
        # Update config
        config.EDGE_VOICE = voice_name
        print(f"✓ Changed voice to: {voice_name}")
        return True
    
    def test_audio_setup(self):
        """Test both TTS and STT"""
        print("\n🎤 Testing Audio Setup...")
        
        # Test TTS
        print("\n1. Testing Text-to-Speech...")
        test_text = "Hello, this is a test of the audio system."
        audio_file = self.text_to_speech(test_text)
        
        if audio_file and os.path.exists(audio_file):
            print(f"   ✓ TTS working! Generated: {audio_file}")
            print(f"   Play this file to verify quality")
        else:
            print(f"   ✗ TTS failed")
        
        # Test STT setup
        print("\n2. Testing Speech-to-Text setup...")
        if self.stt_engine == "faster-whisper":
            try:
                from faster_whisper import WhisperModel
                print(f"   ✓ Faster-Whisper available")
                print(f"   Model: {config.WHISPER_MODEL_SIZE}")
                print(f"   Device: {config.WHISPER_DEVICE}")
            except ImportError:
                print(f"   ✗ Faster-Whisper not installed")
        else:
            try:
                import speech_recognition as sr
                print(f"   ✓ SpeechRecognition available")
            except ImportError:
                print(f"   ✗ SpeechRecognition not installed")
        
        print("\n3. Audio Configuration:")
        print(f"   TTS Engine: {self.tts_engine}")
        print(f"   STT Engine: {self.stt_engine}")
        if self.tts_engine == "edge":
            print(f"   Voice: {config.EDGE_VOICE}")
            print(f"   Rate: {config.EDGE_RATE}")
        
        return audio_file
    
    def get_recommended_voices(self):
        """Get list of recommended high-quality voices"""
        return [
            {
                "name": "en-US-GuyNeural",
                "description": "Male, natural, conversational",
                "recommended_for": "General use, coding discussions"
            },
            {
                "name": "en-US-AriaNeural",
                "description": "Female, friendly, warm",
                "recommended_for": "General use, teaching"
            },
            {
                "name": "en-US-DavisNeural",
                "description": "Male, deep, authoritative",
                "recommended_for": "Professional content, presentations"
            },
            {
                "name": "en-US-JennyNeural",
                "description": "Female, warm, conversational",
                "recommended_for": "Casual conversations"
            },
            {
                "name": "en-GB-RyanNeural",
                "description": "Male, British, professional",
                "recommended_for": "Formal content"
            },
            {
                "name": "en-GB-SoniaNeural",
                "description": "Female, British, clear",
                "recommended_for": "Technical explanations"
            }
        ]

# Global voice handler instance
voice_handler = VoiceHandler()
