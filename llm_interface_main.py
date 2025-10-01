"""
Local LLM Interface with Advanced Features
Supports: Custom UI, Voice Chat, Screen Capture, File Management, Internet Access
Model: mlabonne/gemma-3-27b-it-abliterated
FIXED: Proper CPU offloading for 16GB VRAM
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import json
import os
from datetime import datetime
import threading
import queue
import speech_recognition as sr
from gtts import gTTS
import tempfile
from PIL import ImageGrab, Image
import requests
from bs4 import BeautifulSoup
import pyautogui
import time

# Configuration
class Config:
    MODEL_NAME = "mlabonne/gemma-3-27b-it-abliterated"
    CHAT_HISTORY_DIR = "chat_histories"
    CONTEXT_FILES_DIR = "context_files"
    UPLOADS_DIR = "uploads"
    DOWNLOADS_DIR = "downloads"
    MAX_HISTORY = 50
    
    def __init__(self):
        for dir_path in [self.CHAT_HISTORY_DIR, self.CONTEXT_FILES_DIR, 
                         self.UPLOADS_DIR, self.DOWNLOADS_DIR]:
            os.makedirs(dir_path, exist_ok=True)

config = Config()

# Model Manager - FIXED for RTX 4080 (16GB)
class ModelManager:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        print(f"Loading model on {self.device}...")
        print("Optimizing for RTX 4080 (16GB VRAM)...")
        
        # CRITICAL: Use BitsAndBytesConfig with CPU offload enabled
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            llm_int8_enable_fp32_cpu_offload=True  # KEY FIX - enables CPU offload
        )
        
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        
        print("Loading model (this may take a few minutes)...")
        # Load with proper configuration
        self.model = AutoModelForCausalLM.from_pretrained(
            config.MODEL_NAME,
            quantization_config=quantization_config,
            device_map="auto",  # Auto-distribute across GPU/CPU
            max_memory={
                0: "14GB",      # Reserve safe amount for GPU
                "cpu": "30GB"   # Use system RAM generously
            },
            offload_folder="offload",  # Disk offload if needed
            low_cpu_mem_usage=True,
            torch_dtype=torch.float16
        )
        
        # Enable memory-efficient attention if available
        try:
            from optimum.bettertransformer import BetterTransformer
            self.model = BetterTransformer.transform(self.model)
            print("Memory-efficient attention enabled!")
        except Exception as e:
            print(f"BetterTransformer not available: {e}")
            print("Using standard attention (install optimum for better memory)")
        
        print("Model loaded successfully!")
        if torch.cuda.is_available():
            print(f"GPU Memory allocated: ~{torch.cuda.memory_allocated(0)/1e9:.2f}GB")
            print(f"GPU Memory reserved: ~{torch.cuda.memory_reserved(0)/1e9:.2f}GB")
        
    def generate_response(self, messages, personality_params, context_window=8192):
        if not self.model:
            return "Model not loaded. Please wait..."
        
        # Format messages with emphasis on maintaining context
        prompt = self._format_messages(messages, personality_params, context_window)
        
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt",
            truncation=True,
            max_length=context_window
        ).to(self.device)
        
        # Calculate how many tokens are in the prompt
        prompt_tokens = inputs.input_ids.shape[1]
        max_new = min(
            personality_params.get("max_tokens", 512),
            context_window - prompt_tokens - 50  # Leave buffer
        )
        
        print(f"Generating response (max {max_new} tokens)...")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new,
                temperature=personality_params.get("temperature", 0.7),
                top_p=personality_params.get("top_p", 0.9),
                top_k=personality_params.get("top_k", 50),
                repetition_penalty=personality_params.get("repetition_penalty", 1.1),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=True  # Important for long context
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()
        
        # Clear CUDA cache periodically
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return response
    
    def _format_messages(self, messages, personality_params, context_window):
        system_prompt = personality_params.get("system_prompt", "You are a helpful AI assistant.")
        
        # Calculate token budget for context
        # Roughly estimate 4 chars per token
        available_tokens = context_window - 1024  # Reserve for response
        available_chars = available_tokens * 4
        
        formatted = f"System: {system_prompt}\n\n"
        current_length = len(formatted)
        
        # Add messages from most recent, working backwards
        included_messages = []
        for msg in reversed(messages):
            msg_text = f"{msg['role'].capitalize()}: {msg['content']}\n\n"
            if current_length + len(msg_text) < available_chars:
                included_messages.insert(0, msg_text)
                current_length += len(msg_text)
            else:
                break
        
        formatted += "".join(included_messages)
        formatted += "Assistant: "
        return formatted

model_manager = ModelManager()

# Chat History Manager with Enhanced Memory Features
class ChatHistoryManager:
    def __init__(self):
        self.current_session = None
        self.memory_bank = {}  # Long-term memory across sessions
        
    def create_session(self, personality_params):
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "personality": personality_params,
            "messages": [],
            "context_files": [],
            "memory_summary": "",
            "topics_discussed": [],
            "important_facts": {}
        }
        return session_id
    
    def add_message(self, role, content):
        if self.current_session:
            self.current_session["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            if role == "user":
                self._extract_memory(content)
    
    def _extract_memory(self, content):
        """Extract potential long-term memory items"""
        memory_keywords = ["my name is", "i like", "i prefer", "remember that", 
                          "important:", "note:", "keep in mind"]
        
        content_lower = content.lower()
        for keyword in memory_keywords:
            if keyword in content_lower:
                timestamp = datetime.now().isoformat()
                if "memory_items" not in self.current_session:
                    self.current_session["memory_items"] = []
                self.current_session["memory_items"].append({
                    "content": content,
                    "timestamp": timestamp,
                    "keyword": keyword
                })
    
    def get_context_summary(self):
        """Generate a summary of important context for the current session"""
        if not self.current_session:
            return ""
        
        summary_parts = []
        
        if "memory_items" in self.current_session:
            summary_parts.append("[Important Information]:")
            for item in self.current_session["memory_items"][-5:]:
                summary_parts.append(f"- {item['content']}")
        
        if self.current_session.get("important_facts"):
            summary_parts.append("\n[Key Facts]:")
            for key, value in self.current_session["important_facts"].items():
                summary_parts.append(f"- {key}: {value}")
        
        return "\n".join(summary_parts)
    
    def save_session(self):
        if self.current_session:
            filepath = os.path.join(
                config.CHAT_HISTORY_DIR, 
                f"{self.current_session['id']}.json"
            )
            with open(filepath, 'w') as f:
                json.dump(self.current_session, f, indent=2)
    
    def load_session(self, session_id):
        filepath = os.path.join(config.CHAT_HISTORY_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.current_session = json.load(f)
            return self.current_session
        return None
    
    def list_sessions(self):
        sessions = []
        for filename in os.listdir(config.CHAT_HISTORY_DIR):
            if filename.endswith('.json'):
                sessions.append(filename.replace('.json', ''))
        return sorted(sessions, reverse=True)
    
    def get_all_messages(self, max_tokens=6000):
        """Get all messages within token budget"""
        if not self.current_session:
            return []
        
        messages = self.current_session["messages"]
        max_chars = max_tokens * 4
        
        total_chars = 0
        included = []
        
        for msg in reversed(messages):
            msg_chars = len(msg["content"]) + 20
            if total_chars + msg_chars < max_chars:
                included.insert(0, msg)
                total_chars += msg_chars
            else:
                break
        
        return included

chat_manager = ChatHistoryManager()

# Context File Manager
class ContextFileManager:
    def create_context_file(self, content, name=None):
        if not name:
            name = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(config.CONTEXT_FILES_DIR, name)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def load_context_file(self, name):
        filepath = os.path.join(config.CONTEXT_FILES_DIR, name)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return None
    
    def list_context_files(self):
        return [f for f in os.listdir(config.CONTEXT_FILES_DIR) if f.endswith('.txt')]

context_manager = ContextFileManager()

# Voice Chat Handler with Better TTS
class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        try:
            from TTS.api import TTS
            self.tts_engine = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        except:
            self.tts_engine = "edge"
        
    def speech_to_text(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                try:
                    from faster_whisper import WhisperModel
                    model = WhisperModel("base", device="cuda", compute_type="float16")
                    segments, info = model.transcribe(audio_file)
                    return " ".join([segment.text for segment in segments])
                except:
                    text = self.recognizer.recognize_google(audio)
                    return text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def text_to_speech(self, text):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            if self.tts_engine == "edge":
                import asyncio
                import edge_tts
                
                async def _generate():
                    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
                    await communicate.save(fp.name)
                
                asyncio.run(_generate())
            else:
                self.tts_engine.tts_to_file(text=text, file_path=fp.name)
            
            return fp.name
        except Exception as e:
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en')
                fp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                tts.save(fp_mp3.name)
                return fp_mp3.name
            except:
                return None

voice_handler = VoiceHandler()

# Screen Capture Handler
class ScreenHandler:
    def capture_screen(self):
        screenshot = ImageGrab.grab()
        fp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        screenshot.save(fp.name)
        return fp.name
    
    def describe_screen(self):
        return "Screen captured. (Vision analysis requires additional model)"
    
    def interact_with_screen(self, action, x=None, y=None):
        try:
            if action == "click":
                pyautogui.click(x, y)
                return f"Clicked at ({x}, {y})"
            elif action == "type":
                pyautogui.write(x)
                return f"Typed: {x}"
            elif action == "move":
                pyautogui.moveTo(x, y)
                return f"Moved cursor to ({x}, {y})"
        except Exception as e:
            return f"Error: {str(e)}"

screen_handler = ScreenHandler()

# Internet Access Handler
class InternetHandler:
    def search_web(self, query):
        try:
            url = f"https://www.google.com/search?q={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='g', limit=5)
            
            search_results = []
            for result in results:
                title = result.find('h3')
                if title:
                    search_results.append(title.get_text())
            
            return "\n".join(search_results) if search_results else "No results found"
        except Exception as e:
            return f"Error searching: {str(e)}"
    
    def fetch_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n', strip=True)
            return text[:5000]
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

internet_handler = InternetHandler()

# Main Chat Function
def chat_response(message, history, personality, context_files_selected):
    chat_manager.add_message("user", message)
    
    context = ""
    if context_files_selected:
        for file in context_files_selected:
            content = context_manager.load_context_file(file)
            if content:
                context += f"\n[Context from {file}]:\n{content}\n"
    
    full_message = context + "\n" + message if context else message
    
    messages = [{"role": msg["role"], "content": msg["content"]} 
                for msg in chat_manager.current_session["messages"]]
    
    response = model_manager.generate_response(messages, personality)
    
    chat_manager.add_message("assistant", response)
    chat_manager.save_session()
    
    return response

# Initialize model in background
def init_model():
    model_manager.load_model()

# Gradio Interface
def create_interface():
    with gr.Blocks(title="Local LLM Interface", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Local LLM Interface - Gemma-3-27b-it")
        gr.Markdown("Advanced features: Voice, Screen Control, Internet, Context Files")
        
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(height=500)
                    msg_input = gr.Textbox(
                        label="Message",
                        placeholder="Type your message...",
                        lines=3
                    )
                    with gr.Row():
                        send_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear")
                    
                    with gr.Accordion("Voice Input", open=False):
                        audio_input = gr.Audio(source="microphone", type="filepath")
                        voice_btn = gr.Button("Process Voice")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Personality Settings")
                    system_prompt = gr.Textbox(
                        label="System Prompt",
                        value="You are a helpful AI assistant.",
                        lines=3
                    )
                    temperature = gr.Slider(0.1, 2.0, value=0.7, label="Temperature")
                    max_tokens = gr.Slider(128, 4096, value=1024, step=128, label="Max Tokens")
                    top_p = gr.Slider(0.1, 1.0, value=0.9, label="Top P")
                    top_k = gr.Slider(1, 100, value=50, step=1, label="Top K")
                    repetition_penalty = gr.Slider(1.0, 2.0, value=1.1, step=0.1, label="Repetition Penalty")
                    context_window = gr.Slider(2048, 8192, value=8192, step=1024, label="Context Window")
                    
                    gr.Markdown("### Context Files")
                    context_files = gr.CheckboxGroup(
                        choices=context_manager.list_context_files(),
                        label="Select Context Files"
                    )
                    refresh_context_btn = gr.Button("Refresh List")
        
        with gr.Tab("Screen Control"):
            with gr.Row():
                capture_btn = gr.Button("Capture Screen")
                screen_img = gr.Image(label="Screenshot")
            
            gr.Markdown("### Screen Interaction")
            with gr.Row():
                action_type = gr.Dropdown(
                    ["click", "type", "move"],
                    label="Action",
                    value="click"
                )
                coord_x = gr.Number(label="X Coordinate", value=100)
                coord_y = gr.Number(label="Y Coordinate", value=100)
            interact_btn = gr.Button("Execute Action")
            action_output = gr.Textbox(label="Result")
        
        with gr.Tab("Internet"):
            gr.Markdown("### Web Search")
            search_query = gr.Textbox(label="Search Query")
            search_btn = gr.Button("Search")
            search_results = gr.Textbox(label="Results", lines=10)
            
            gr.Markdown("### Fetch URL")
            url_input = gr.Textbox(label="URL")
            fetch_btn = gr.Button("Fetch Content")
            url_content = gr.Textbox(label="Content", lines=10)
        
        with gr.Tab("Files"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Upload Files")
                    file_upload = gr.File(label="Upload", file_count="multiple")
                    upload_btn = gr.Button("Process Upload")
                
                with gr.Column():
                    gr.Markdown("### Context Files")
                    context_name = gr.Textbox(label="File Name")
                    context_content = gr.Textbox(label="Content", lines=10)
                    save_context_btn = gr.Button("Save Context File")
        
        with gr.Tab("History"):
            session_list = gr.Dropdown(
                choices=chat_manager.list_sessions(),
                label="Load Session"
            )
            load_session_btn = gr.Button("Load")
            new_session_btn = gr.Button("New Session", variant="primary")
        
        return demo

# Start the application
if __name__ == "__main__":
    print("=" * 60)
    print("Starting Local LLM Interface")
    print("=" * 60)
    print("Checking GPU...")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("GPU: Not available (CPU mode)")
    
    print("Setting high priority...")
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.HIGH_PRIORITY_CLASS if os.name == 'nt' else -10)
    except:
        print("Value map does not contain the input value for this property.")
    
    print("Starting application...")
    
    # Start model loading in background
    print("Loading model in background...")
    model_thread = threading.Thread(target=init_model)
    model_thread.start()
    
    # Create default session
    default_personality = {
        "system_prompt": "You are a helpful AI assistant.",
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "top_k": 50,
        "repetition_penalty": 1.1,
        "context_window": 8192
    }
    chat_manager.create_session(default_personality)
    
    # Create and launch interface
    print("=" * 60)
    print("Interface will be available at: http://127.0.0.1:7860")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )