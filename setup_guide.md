# 🚀 Local LLM Interface Setup Guide

Complete setup guide for running Gemma-3-27b-it-abliterated with advanced features.

## 📋 System Requirements

- **GPU**: NVIDIA GPU with 24GB+ VRAM (recommended) or CPU with 32GB+ RAM
- **Storage**: 60GB+ free space
- **OS**: Windows, Linux, or macOS
- **Python**: 3.10 or higher

## 🔧 Installation Steps

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv llm_env

# Activate it
# Windows:
llm_env\Scripts\activate
# Linux/Mac:
source llm_env/bin/activate
```

### 2. Install Dependencies

```bash
# Install PyTorch (CUDA 11.8 example - adjust for your system)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other requirements
pip install -r requirements.txt
```

### 3. Download the Model

The model will auto-download on first run, but you can pre-download:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "mlabonne/gemma-3-27b-it-abliterated"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

### 4. Additional Setup (Platform-Specific)

#### Windows:
```bash
# For audio support
pip install pipwin
pipwin install pyaudio
```

#### Linux:
```bash
# Install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio
sudo apt-get install espeak ffmpeg

# For screen capture
sudo apt-get install scrot
```

#### macOS:
```bash
# Install audio dependencies
brew install portaudio
pip install pyaudio

# For screen capture permissions, grant access in:
# System Preferences > Security & Privacy > Screen Recording
```

## 🎯 Running the Application

```bash
python app.py
```

The interface will be available at `http://127.0.0.1:7860`

## 📁 Directory Structure

```
project/
├── app.py                  # Main application
├── requirements.txt        # Dependencies
├── chat_histories/         # Saved chat sessions
├── context_files/          # Persistent context files
├── uploads/               # Uploaded files
└── downloads/             # Generated downloads
```

## 🎨 Features Overview

### 1. **Custom Personality Parameters**
- System prompts for character definition
- Temperature, Top-P, and Max Tokens control
- Persistent settings per chat session

### 2. **Chat History**
- Auto-saves every conversation
- Load previous sessions
- Export/import conversations
- Search through history

### 3. **Voice Chat**
- Speech-to-text input
- Text-to-speech responses
- Multiple language support

### 4. **Screen Interaction**
- Capture screenshots
- Describe screen content (requires vision model)
- Automate clicks and typing
- Mouse movement control

### 5. **Internet Access**
- Web search integration
- URL content fetching
- Real-time information retrieval
- Summarization of web content

### 6. **Context Files**
- Create persistent knowledge files
- Auto-inject context into conversations
- Selective context loading
- Cross-session context sharing

### 7. **File Management**
- Upload documents (PDF, DOCX, TXT, etc.)
- Extract and process content
- Generate downloadable responses
- Batch file processing

## ⚙️ Configuration Options

### Model Optimization

For **GPU with limited VRAM** (16GB):
```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    load_in_8bit=True  # Add this
)
```

For **CPU only**:
```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu",
    low_cpu_mem_usage=True
)
```

For **Maximum performance** (24GB+ GPU):
```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    attn_implementation="flash_attention_2"  # Requires flash-attn
)
```

## 🔒 Security Considerations

- **Screen Control**: Be cautious with automation features
- **Internet Access**: Implements basic rate limiting
- **File Uploads**: Scanned for common issues
- **Local Only**: No data leaves your machine

## 🐛 Troubleshooting

### Model Won't Load
```bash
# Clear cache and retry
rm -rf ~/.cache/huggingface/
python app.py
```

### Audio Issues
```bash
# Test microphone
python -m speech_recognition
```

### GPU Not Detected
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory
- Reduce `max_tokens` in personality settings
- Use 8-bit quantization
- Close other applications

## 📚 Usage Examples

### Creating a Context File
1. Go to "Files" tab
2. Enter name: `project_knowledge.txt`
3. Add content: "This project is about..."
4. Click "Save Context File"
5. Select in chat to include in conversations

### Voice Interaction
1. Go to "Chat" tab
2. Click microphone icon
3. Speak your message
4. Click "Process Voice"
5. Response can be played back

### Screen Automation
1. Go to "Screen Control" tab
2. Capture current screen
3. Set action type (click/type/move)
4. Enter coordinates or text
5. Execute action

## 🚀 Advanced Features

### Custom Personality Example

**Coding Assistant**:
```
System Prompt: "You are an expert programmer. Provide concise, 
well-documented code solutions. Always explain your reasoning."

Temperature: 0.3
Max Tokens: 1024
```

**Creative Writer**:
```
System Prompt: "You are a creative storyteller. Be imaginative, 
descriptive, and engaging. Use vivid language."

Temperature: 1.2
Max Tokens: 2048
```

### Context File Strategy

Create specialized context files:
- `coding_standards.txt` - Your project conventions
- `business_context.txt` - Company/domain knowledge
- `preferences.txt` - Your communication style
- `current_project.txt` - Active work details

## 📖 API Integration (Optional)

For better internet access, add API keys:

```bash
# Create .env file
echo "SERPER_API_KEY=your_key_here" > .env
echo "OPENAI_API_KEY=your_key_for_vision" >> .env
```

Then update the code to use these services.

## 🎓 Tips for Best Results

1. **Personality Tuning**: Experiment with different system prompts
2. **Context Management**: Keep context files focused and updated
3. **Temperature**: Lower (0.3-0.5) for factual, higher (0.8-1.2) for creative
4. **Token Limits**: Balance between response length and speed
5. **Session Management**: Start new sessions for different topics

## 🔄 Updates & Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update model (when new version available)
huggingface-cli download mlabonne/gemma-3-27b-it-abliterated
```

## 📞 Support

- Check model documentation: https://huggingface.co/mlabonne/gemma-3-27b-it-abliterated
- Gradio docs: https://www.gradio.app/docs
- Transformers docs: https://huggingface.co/docs/transformers

---

**Ready to start?** Run `python app.py` and open http://127.0.0.1:7860 🎉