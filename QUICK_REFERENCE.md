# ⚡ Quick Reference Card

## 🚀 Installation & Launch

```batch
# First time setup
install_windows.bat

# Every time launch
launch.bat

# Open browser
http://127.0.0.1:7860
```

## 📊 Context Monitoring

| Status | What It Means | Action |
|--------|---------------|--------|
| 💾 30% | Plenty of room | Use freely |
| 💾 70% | Getting full | Be aware |
| ⚠️ 85% | Warning shown | Continue or summarize |
| 🔴 92% | Auto-creates summary | Keeps going automatically |

**Location:** Chat tab → Right sidebar → Context Usage

## 🎨 Personality Quick Sets

```yaml
# Direct & Technical (Your Style)
Preset: "coding_buddy"
Directness: 90, Technicality: 95

# Patient Teacher
Preset: "teacher"
Supportiveness: 85, Verbosity: 80

# Fast Research
Preset: "researcher"
Formality: 70, Assertiveness: 90
```

## 📁 Context Files Workflow

### Create
```
1. Files tab
2. Name: my_preferences.txt
3. Content: [Your info]
4. Save
```

### Use
```
1. Chat tab
2. Right sidebar → Context Files
3. Check boxes to load
4. Model has instant access!
```

### Auto-Generated
```
Location: context_files/auto_generated/
Created: When context hits 90%
Contains: Conversation summary
Use: Load in future sessions
```

## 🎤 Voice Commands

### Input
```
1. Click mic icon
2. Speak
3. Click "Transcribe to Text"
4. Send message
```

### Output
```
1. Get response
2. Click "🔊 Read Last"
3. Listen to natural voice
```

### Change Voice
```
Edit: system_config.yaml
voice: "en-US-GuyNeural"  # Male
voice: "en-US-AriaNeural" # Female
```

## 🌐 Internet Access

### Search
```
Internet tab → Search Query → Search
Returns: 5 results with snippets
```

### Fetch URL
```
Internet tab → URL → Fetch Content
Returns: Clean text from page
```

### In Chat
```
"Search for latest Python features"
"Fetch content from [URL]"
```

## 🖥️ Screen Control

### Capture
```
Screen Control tab → Capture Screenshot
Result: Image appears
```

### Automate
```
Action: click / type / move
Coordinates: X, Y
Execute Action
```

### Safety
```
Failsafe: Move mouse to corner
Confirmation: Enabled by default
```

## 💾 Session Management

### Save
```
Auto-saves: Every 5 messages
Manual: History tab → Save
```

### Load
```
History tab → Select session → Load
Result: Conversation restored
```

### Export
```
Session → Export → TXT/MD/JSON
```

## ⚙️ Settings Quick Adjust

### Speed Up
```
Context Window: 8192 (smaller)
Max Tokens: 512 (shorter)
Temperature: 0.3 (focused)
```

### Maximum Quality
```
Context Window: 16384 (maximum)
Max Tokens: 2048 (detailed)
Temperature: 0.7 (balanced)
```

### All-Day Session
```
Context Window: 16384 (max)
Auto-context: Enabled (default)
Max Tokens: 1024 (balanced)
```

## 🔧 Common Tasks

### Switch Topics
```
1. Create context summary (manual)
2. Clear chat
3. Start new topic
4. Old topic saved for later
```

### Load Project Context
```
1. Check: my_prefs.txt
2. Check: project_spec.txt  
3. Check: api_docs.txt
4. Start coding!
```

### End of Day
```
1. "Summarize today's work"
2. Save as: today_summary.txt
3. Tomorrow: Load summary
4. Continue seamlessly
```

### Debug Session
```
1. Load: codebase_context.txt
2. Paste error
3. Full debugging with context
4. Model remembers all files
```

## 📝 Memory Triggers

Use these phrases to auto-store info:

```
"My name is..."
"I prefer..."
"Remember that..."
"Important:"
"Always..."
"Never..."
"I work with..."
"I use..."
```

## 🐛 Quick Fixes

### Model Won't Load
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"
# Should show: True

# If False:
# 1. Restart PC
# 2. Check NVIDIA drivers
# 3. Reinstall PyTorch
```

### Out of Memory
```yaml
# Reduce in settings:
context_window: 8192  # From 16384
max_tokens: 768       # From 1024
```

### Slow Responses
```yaml
# Trade context for speed:
context_window: 8192
max_tokens: 512
```

### Audio Not Working
```bash
# Test Edge TTS
edge-tts --text "test" --voice en-US-GuyNeural --write-media test.mp3

# Check microphone
Windows Settings → Privacy → Microphone → Allow
```

### Context Files Missing
```
1. Check: context_files/ directory exists
2. Click: Refresh List
3. Files must be .txt format
4. Check encoding: UTF-8
```

## 📂 File Locations

```
project/
├── app.py              # Main app
├── system_config.yaml  # YOUR SETTINGS
├── chat_histories/     # Saved chats
├── context_files/      # Knowledge base
│   └── auto_generated/ # Auto-summaries
├── uploads/            # Your uploads
├── downloads/          # Generated files
└── logs/               # Debug logs
```

## 🎯 Hotkeys & Shortcuts

### In Chat
```
Enter:           Send message
Shift+Enter:     New line
Ctrl+K:          Clear chat
```

### In UI
```
Tab:             Next field
Shift+Tab:       Previous field
Space:           Toggle checkbox
```

## 💡 Pro Tips

### 1. Pre-load Context
```
Morning: Load daily_goals.txt
Result: Model knows your agenda
```

### 2. Name Files Well
```
Bad:  notes.txt
Good: project_alpha_api_spec.txt
```

### 3. Use Categories
```
personal/
projects/
learning/
reference/
```

### 4. Leverage Auto-Context
```
Don't worry about limits
Let system auto-manage
Review summaries weekly
```

### 5. Set Defaults
```
Edit: system_config.yaml
Set: Your preferred values
Restart: Applied automatically
```

## 🔍 Status Indicators

```
✓  Success
⚠️  Warning
🔴 Critical
💾 Context usage
📄 File created
🟢 Healthy (0-79%)
🟡 Warning (80-89%)
🔴 Auto-create (90%+)
```

## 📞 Help Resources

```
Documentation: See all .md files in project
Model Info: huggingface.co/mlabonne/gemma-3-27b-it-abliterated
Gradio: gradio.app/docs
Issues: Check logs/ directory
```

## ⚡ Most Common Workflows

### Coding Session
```
1. Load project context files
2. Set personality: "coding_buddy"
3. Context: 16384 tokens
4. Code all day
5. Auto-summaries handle overflow
```

### Research Mode
```
1. Internet tab → Search
2. Fetch multiple URLs
3. Synthesize in chat
4. Save as context file
```

### Learning Path
```
1. Load study notes
2. Set personality: "teacher"
3. Ask questions
4. Create summary context file
5. Load summary next session
```

---

**Print this page and keep it handy!** 📋