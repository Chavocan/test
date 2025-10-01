# 🎤 Audio Setup Guide - High Quality TTS

## Why Edge TTS is Better (No Piper!)

**Piper TTS:** Robotic, unpleasant, sounds like old text-to-speech

**Edge TTS (What we use):** 
- Microsoft's neural voices
- Sounds completely natural
- Same voices used in Windows 11
- Multiple accents and genders

## 🔊 Recommended Voice Options

### Best General-Purpose Voices

**English (US) - Female:**
- **`en-US-AriaNeural`** ⭐ Recommended - Friendly, natural
- `en-US-JennyNeural` - Warm, conversational
- `en-US-SaraNeural` - Professional, clear

**English (US) - Male:**
- **`en-US-GuyNeural`** ⭐ Recommended - Natural, pleasant
- `en-US-DavisNeural` - Deep, authoritative
- `en-US-TonyNeural` - Professional narrator

**English (UK):**
- `en-GB-SoniaNeural` - British female, clear
- `en-GB-RyanNeural` - British male, professional

### How to Change Voice

Edit `system_config.yaml`:

```yaml
audio:
  tts_engine: "edge"
  edge:
    voice: "en-US-GuyNeural"  # Change this line
    rate: "+0%"
    volume: "+0%"
```

### Voice Speed Adjustment

**Faster:**
```yaml
rate: "+20%"  # 20% faster
```

**Slower:**
```yaml
rate: "-20%"  # 20% slower
```

**Normal:**
```yaml
rate: "+0%"   # Default speed
```

## 🎵 Alternative: Coqui TTS (Highest Quality)

If you want **maximum quality** (but slower generation):

### Installation
```bash
pip install TTS
```

### Configuration
```yaml
audio:
  tts_engine: "coqui"
  coqui:
    model: "tts_models/en/ljspeech/tacotron2-DDC"
```

### Coqui Models

**Fast & Good:**
- `tts_models/en/ljspeech/tacotron2-DDC`
- `tts_models/en/ljspeech/glow-tts`

**Slower but Amazing:**
- `tts_models/en/vctk/vits` - Multiple voices
- `tts_models/en/ljspeech/vits` - Single high-quality voice

**Multi-language:**
- `tts_models/multilingual/multi-dataset/xtts_v2` - Supports 16+ languages

## 🎙️ Speech Recognition Setup

### Faster-Whisper (Recommended)

**Best balance of speed and accuracy:**

```yaml
audio:
  stt_engine: "faster-whisper"
  whisper:
    model_size: "base"      # Options: tiny, base, small, medium, large
    device: "cuda"          # Use your RTX 4080!
    compute_type: "float16"
    language: "en"
```

### Model Size Guide

| Model | VRAM | Speed | Accuracy |
|-------|------|-------|----------|
| tiny  | ~1GB | Very Fast | Good |
| base  | ~1GB | Fast | Better ⭐ |
| small | ~2GB | Medium | Great |
| medium| ~5GB | Slow | Excellent |
| large | ~10GB| Slowest | Best |

**Recommendation:** Start with `base`, upgrade to `small` or `medium` if you need better accuracy.

## 🔧 Testing Your Audio Setup

### Test TTS

```python
# Run this in Python console
import edge_tts
import asyncio

async def test():
    tts = edge_tts.Communicate(
        "Hello! This is a test of the audio system.", 
        "en-US-GuyNeural"
    )
    await tts.save("test.mp3")

asyncio.run(test())
```

Then play `test.mp3` - should sound natural!

### Test STT

```python
# Record and test speech recognition
import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)
    
print("You said:", r.recognize_google(audio))
```

## 🎛️ Audio Quality Settings

### For Best Quality (Your System Can Handle It)

```yaml
audio:
  tts_engine: "edge"
  edge:
    voice: "en-US-GuyNeural"
    rate: "+0%"
    volume: "+0%"
    pitch: "+0Hz"  # Optional pitch adjustment
  
  stt_engine: "faster-whisper"
  whisper:
    model_size: "medium"  # Use medium for better accuracy
    device: "cuda"        # Your RTX 4080
    compute_type: "float16"
    beam_size: 5          # Higher = more accurate, slower
    language: "en"
```

### For Fastest Response

```yaml
audio:
  tts_engine: "edge"  # Already very fast
  edge:
    voice: "en-US-GuyNeural"
  
  stt_engine: "faster-whisper"
  whisper:
    model_size: "tiny"  # Fastest option
    device: "cuda"
```

## 🌍 Multi-Language Support

### English + Spanish
```yaml
whisper:
  language: null  # Auto-detect
  # Or specific:
  # language: "es"  # Spanish
  # language: "en"  # English
```

### Available Edge TTS Languages

- English (US, UK, AU, CA, IN, etc.)
- Spanish (ES, MX, AR, etc.)
- French (FR, CA)
- German (DE)
- Italian (IT)
- Portuguese (PT, BR)
- Chinese (ZH-CN, ZH-TW)
- Japanese (JA)
- Korean (KO)
- And 40+ more!

Full list: [Microsoft Edge TTS Voices](https://speech.microsoft.com/portal/voicegallery)

## 📊 Performance Expectations (Your System)

### TTS Generation Speed

**Edge TTS:**
- ~0.5-1 second for short responses
- ~2-3 seconds for long responses
- ⚡ Very fast, runs on CPU

**Coqui TTS:**
- ~2-4 seconds for short responses
- ~5-10 seconds for long responses
- 🐌 Slower but highest quality

### STT Recognition Speed

**Faster-Whisper (base) on RTX 4080:**
- ~0.5 seconds per 10 seconds of audio
- ⚡ Real-time or faster!

**Faster-Whisper (medium) on RTX 4080:**
- ~1-2 seconds per 10 seconds of audio
- Still very fast with better accuracy

## 🎯 Recommended Setup for You

```yaml
# Optimal for RTX 4080 + quality focus
audio:
  # TTS: Edge (fast, natural, free)
  tts_engine: "edge"
  edge:
    voice: "en-US-GuyNeural"  # Or AriaNeural for female
    rate: "+0%"
    volume: "+0%"
  
  # STT: Faster-Whisper medium (accurate + fast on your GPU)
  stt_engine: "faster-whisper"
  whisper:
    model_size: "medium"
    device: "cuda"
    compute_type: "float16"
    language: "en"
```

**Why this setup:**
- ✅ Edge TTS is **free** and sounds **human**
- ✅ Your RTX 4080 handles Whisper medium easily
- ✅ No robotic Piper voices!
- ✅ Better accuracy than Google STT
- ✅ Works offline (after initial model download)

## 🚫 Avoiding Piper

The system **does not** and **will not** use Piper TTS. Your audio pipeline is:

1. **Speech Input** → Faster-Whisper → Text
2. **Text Output** → Edge TTS → Natural Speech

No robotic voices. Ever. 🎉

## 🔊 Testing Before First Use

1. **Test microphone:**
   ```bash
   python -m speech_recognition
   # Speak when prompted
   ```

2. **Test Edge TTS:**
   ```bash
   edge-tts --text "Testing audio quality" --voice en-US-GuyNeural --write-media test.mp3
   # Play test.mp3
   ```

3. **Test Faster-Whisper:**
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel("base", device="cuda")
   # Should load without errors
   ```

## 💡 Pro Tips

1. **Adjust speaking rate** based on content type:
   - Technical explanations: `-10%` (slower)
   - General conversation: `+0%` (normal)
   - Quick updates: `+10%` (faster)

2. **Use different voices** for different purposes:
   - Coding: Male voice (GuyNeural)
   - Writing: Female voice (AriaNeural)
   - News/Updates: Professional voice (DavisNeural)

3. **Background noise?** Adjust Whisper:
   ```yaml
   whisper:
     model_size: "medium"  # Better at handling noise
   ```

4. **Voice chat workflow:**
   - Click mic → Speak → Auto-transcribe → Get response → Auto-play audio
   - Seamless conversation flow!

## 📞 Audio Troubleshooting

### "No sound output"

**Check:**
1. Windows audio output device
2. File actually generated (check `temp/` folder)
3. Try different voice

### "Microphone not detected"

**Check:**
1. Windows Privacy Settings → Microphone → Allow apps
2. Run: `python -m speech_recognition` to test
3. Try different microphone in Windows settings

### "Whisper is slow"

**Solutions:**
1. Use smaller model (`base` instead of `medium`)
2. Check if CUDA is being used:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   ```

### "Edge TTS not working"

**Solutions:**
1. Check internet connection (needs to download on first use)
2. Try: `pip install --upgrade edge-tts`
3. Test with command line tool first

## 🎨 Voice Customization Examples

### Professional Presentation
```yaml
voice: "en-US-DavisNeural"
rate: "-5%"  # Slightly slower
volume: "+5%"  # Slightly louder
```

### Casual Chat
```yaml
voice: "en-US-AriaNeural"
rate: "+5%"  # Slightly faster
volume: "+0%"
```

### Technical Tutorial
```yaml
voice: "en-GB-SoniaNeural"  # British, clear
rate: "-10%"  # Slower for clarity
volume: "+0%"
```

## 🌟 Advanced Features

### Multiple Voice Support

You can switch voices on the fly in the UI (future feature) or by editing config:

```yaml
voices:
  default: "en-US-GuyNeural"
  technical: "en-GB-RyanNeural"
  casual: "en-US-AriaNeural"
```

### Voice Emotion Control (Edge TTS)

Some voices support style/emotion:

```yaml
# Example (if supported by voice)
style: "cheerful"  # or "sad", "angry", "excited"
```

### Whisper Language Auto-Detection

```yaml
whisper:
  language: null  # Auto-detect language
```

Great for multilingual conversations!

## 📚 Additional Resources

- **Edge TTS Voices:** https://speech.microsoft.com/portal/voicegallery
- **Faster-Whisper:** https://github.com/guillaumekln/faster-whisper
- **Coqui TTS:** https://github.com/coqui-ai/TTS

---

**Ready for natural-sounding AI conversations? No Piper in sight! 🎤✨**