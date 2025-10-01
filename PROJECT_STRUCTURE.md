# 📁 Project Structure

## Complete File Organization

```
LocalLLM/
│
├── 📄 Core Application Files
│   ├── app.py                      # Main application (runs everything)
│   ├── config.py                   # Configuration management
│   ├── model_manager.py            # Model loading & generation
│   ├── chat_manager.py             # Chat history & memory
│   ├── context_manager.py          # Context files management
│   ├── personality.py              # Personality system (vibes/emotions)
│   ├── audio_handler.py            # Voice processing (NO PIPER!)
│   ├── screen_handler.py           # Screen capture & automation
│   └── internet_handler.py         # Web search & content fetching
│
├── ⚙️ Configuration Files
│   ├── system_config.yaml          # User configuration (EDIT THIS!)
│   ├── requirements.txt            # Python dependencies
│   └── .env (optional)             # API keys if needed
│
├── 🚀 Installation & Launch
│   ├── install_windows.bat         # One-click Windows install
│   ├── launch.bat                  # Quick launch script
│   └── README.md                   # Getting started guide
│
├── 📚 Documentation
│   ├── QUICK_START.md              # First 10 minutes guide
│   ├── Memory_Context_Guide.md    # Master context files
│   ├── Audio_Setup_Guide.md       # Perfect audio (no Piper!)
│   └── PROJECT_STRUCTURE.md       # This file
│
├── 📁 Data Directories (auto-created)
│   ├── chat_histories/             # Saved conversations
│   ├── context_files/              # Persistent knowledge
│   │   ├── personal/              # Your preferences
│   │   ├── projects/              # Project-specific info
│   │   ├── learning/              # Study notes
│   │   └── reference/             # Quick reference
│   ├── uploads/                    # Uploaded files
│   ├── downloads/                  # Generated downloads
│   ├── logs/                       # Application logs
│   ├── .cache/                     # Cached data
│   ├── temp/                       # Temporary files
│   └── model_offload/             # Model CPU offload
│
└── 🔧 Virtual Environment
    └── llm_env/                    # Python virtual environment

## 🔧 Modular Architecture Benefits

### Why Files Are Split Up

1. **Easy Updates**: Change one feature without breaking others
2. **Clear Responsibilities**: Each module has one job
3. **Debug Friendly**: Know exactly where to look for issues
4. **Customizable**: Swap modules without touching core code

### Module Dependencies

```
app.py (main)
  ├─> config.py (settings)
  ├─> model_manager.py
  │     └─> config.py
  ├─> chat_manager.py
  │     └─> config.py
  ├─> context_manager.py
  │     └─> config.py
  ├─> personality.py (standalone)
  ├─> audio_handler.py
  │     └─> config.py
  ├─> screen_handler.py
  │     └─> config.py
  └─> internet_handler.py
        └─> config.py
```

## 📝 File Descriptions

### Core Files

**app.py** - Main application
- Gradio UI setup
- Event handlers
- Ties all modules together
- ~500 lines

**config.py** - Configuration
- All settings in one place
- Loads from system_config.yaml
- Directory management
- ~200 lines

**model_manager.py** - LLM Model
- Model loading with quantization
- Text generation
- Memory optimization for RTX 4080
- ~250 lines

**chat_manager.py** - Conversations
- Session management
- Message history
- Memory extraction (auto-learns preferences)
- Export/import sessions
- ~300 lines

**context_manager.py** - Knowledge Base
- Create/read/update/delete context files
- Category organization
- Search functionality
- Token budget management
- ~250 lines

**personality.py** - Tone/Vibes System
- Define personality through dimensions
- NO scripted responses
- Pre-built presets
- Custom personality builder
- ~300 lines

**audio_handler.py** - Voice Processing
- Edge TTS (Microsoft voices - NATURAL!)
- Faster-Whisper (GPU-accelerated STT)
- Multiple engine support
- NO PIPER EVER!
- ~250 lines

**screen_handler.py** - Screen Automation
- Screenshot capture
- Click/type/move automation
- Safety features
- Image recognition
- ~200 lines

**internet_handler.py** - Web Access
- DuckDuckGo search
- URL content fetching
- Link extraction
- Metadata parsing
- ~250 lines

## 🎯 Key Features by Module

### Model Manager
- ✅ 4-bit quantization for 16GB GPU
- ✅ Smart context window management
- ✅ Token budget calculation
- ✅ CUDA cache management

### Chat Manager
- ✅ Auto-save every N messages
- ✅ Memory extraction from keywords
- ✅ Export as TXT/MD/JSON
- ✅ Session statistics

### Context Manager
- ✅ Category organization
- ✅ File caching
- ✅ Search across files
- ✅ Token-aware loading

### Personality System
- ✅ 8 personality dimensions
- ✅ 7 pre-built presets
- ✅ Custom personality builder
- ✅ Anti-scripting built-in

### Audio Handler
- ✅ Edge TTS (best quality)
- ✅ Faster-Whisper (accurate)
- ✅ Voice selection
- ✅ Fallback engines

## 🔄 How to Modify Components

### Want to change the model?
**Edit:** `config.py` or `system_config.yaml`
```python
MODEL_NAME = "your-model-name"
```

### Want different audio voices?
**Edit:** `system_config.yaml`
```yaml
audio:
  edge:
    voice: "en-US-GuyNeural"  # Change this
```

### Want to adjust memory behavior?
**Edit:** `chat_manager.py`
```python
self.memory_keywords = [
    "remember",
    "important",
    # Add your keywords
]
```

### Want custom personality dimensions?
**Edit:** `personality.py`
```python
PERSONALITY_DIMENSIONS = {
    "your_dimension": {
        "name": "Your Trait",
        "low": "Description",
        "high": "Description",
        "default": 50
    }
}
```

### Want different UI layout?
**Edit:** `app.py` - build_interface() function

### Want to add new features?
**Create new module:** `your_feature.py`
**Import in:** `app.py`
**Add to UI:** `build_interface()`

## 🚀 Quick Reference

### Starting the App
```batch
launch.bat
```

### Stopping the App
```
Ctrl + C in terminal
```

### Updating Config
1. Edit `system_config.yaml`
2. Restart app
3. Changes take effect

### Adding Context Files
1. Go to "Context Files" tab in UI
2. Create file with name/content
3. Auto-available in all sessions

### Checking Logs
```
logs/ directory
```

### Clearing Cache
```python
# In app, or manually:
rm -rf .cache/
rm -rf temp/
```

## 📊 File Sizes (Approximate)

| File | Lines | Purpose |
|------|-------|---------|
| app.py | 500 | Main UI & logic |
| config.py | 200 | Settings |
| model_manager.py | 250 | LLM handling |
| chat_manager.py | 300 | Conversations |
| context_manager.py | 250 | Knowledge files |
| personality.py | 300 | Tone system |
| audio_handler.py | 250 | Voice |
| screen_handler.py | 200 | Automation |
| internet_handler.py | 250 | Web access |
| **Total** | **~2500** | **All code** |

## 🎨 Customization Examples

### Example 1: Add Custom Voice
**File:** `audio_handler.py`
```python
def _custom_tts_engine(self, text):
    # Your custom TTS code here
    pass
```

### Example 2: Custom Memory Trigger
**File:** `chat_manager.py`
```python
if "this is critical" in content_lower:
    # Store with high priority
    self.current_session["critical_items"].append(content)
```

### Example 3: New Personality Preset
**File:** `personality.py`
```python
"your_preset": {
    "name": "Your Style",
    "description": "Your description",
    "dimensions": {
        "formality": 40,
        "directness": 80,
        # ... etc
    }
}
```

## 🐛 Troubleshooting by File

| Issue | Check File | Look For |
|-------|-----------|----------|
| Model won't load | model_manager.py | CUDA, memory settings |
| Audio not working | audio_handler.py | TTS/STT engine config |
| Context files missing | context_manager.py | Directory paths |
| Chat history gone | chat_manager.py | Auto-save settings |
| UI broken | app.py | Gradio event handlers |
| Settings not applying | config.py | YAML loading |

## 📦 Dependencies by Module

**Model Manager:**
- torch
- transformers
- bitsandbytes
- accelerate

**Audio Handler:**
- edge-tts
- faster-whisper
- SpeechRecognition

**Screen Handler:**
- pyautogui
- pillow

**Internet Handler:**
- requests
- beautifulsoup4
- duckduckgo-search

**UI (app.py):**
- gradio

**Config:**
- pyyaml

## 🎯 Development Workflow

1. **Make changes** to individual module
2. **Test module** independently if possible
3. **Restart app** to see changes
4. **Check logs** if issues arise
5. **Commit changes** to version control

## 💡 Pro Tips

1. **Edit system_config.yaml** instead of hardcoding changes
2. **Create custom context files** for domain-specific knowledge
3. **Use personality presets** as starting points
4. **Check logs/** directory for debugging
5. **Backup chat_histories/** before major changes

---

**Your system is now fully modular and easy to modify! 🎉**

Each file has a single, clear purpose. Change what you need without breaking what you don't.
