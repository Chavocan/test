"""
Configuration Module
Handles all application settings and paths
"""

import os
import yaml
from pathlib import Path

class Config:
    """Main configuration class"""
    
    # Model settings
    MODEL_NAME = "./model_cache"
    
    # Directory paths
    BASE_DIR = Path(__file__).parent
    CHAT_HISTORY_DIR = BASE_DIR / "chat_histories"
    CONTEXT_FILES_DIR = BASE_DIR / "context_files"
    UPLOADS_DIR = BASE_DIR / "uploads"
    DOWNLOADS_DIR = BASE_DIR / "downloads"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = BASE_DIR / ".cache"
    TEMP_DIR = BASE_DIR / "temp"
    OFFLOAD_DIR = BASE_DIR / "model_offload"
    
    # Model configuration
    QUANTIZATION_BITS = 4
    QUANTIZATION_TYPE = "nf4"
    USE_DOUBLE_QUANT = True
    COMPUTE_DTYPE = "float16"
    
    # Context settings - MAXIMIZED for 64GB RAM + RTX 4080
    MAX_CONTEXT_LENGTH = 16384  # 16K tokens! (~65,000 characters)
    DEFAULT_CONTEXT_LENGTH = 12288  # 12K default (~49,000 characters)
    RESERVE_FOR_RESPONSE = 2048  # More room for detailed responses
    
    # Memory allocation
    GPU_MAX_MEMORY = "15GB"
    CPU_MAX_MEMORY = "32GB"
    DISK_MAX_MEMORY = "128GB"
    
    # Generation defaults
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 50
    DEFAULT_REPETITION_PENALTY = 1.1
    DEFAULT_MAX_TOKENS = 512
    
    # Chat history
    MAX_MESSAGES_IN_MEMORY = 100
    AUTO_SAVE_INTERVAL = 5
    
    # Context files
    MAX_CONTEXT_FILES = 10
    CONTEXT_TOKEN_BUDGET = 2048
    
    # Audio settings
    TTS_ENGINE = "edge"  # Options: edge, coqui, gtts
    STT_ENGINE = "faster-whisper"  # Options: faster-whisper, google
    
    EDGE_VOICE = "en-US-GuyNeural"
    EDGE_RATE = "+0%"
    EDGE_VOLUME = "+0%"
    
    WHISPER_MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large
    WHISPER_DEVICE = "cuda"
    WHISPER_COMPUTE_TYPE = "float16"
    
    # UI settings
    UI_PORT = 7860
    UI_SERVER = "127.0.0.1"
    UI_SHARE = False
    UI_THEME = "soft"

    # Internet settings
    SEARCH_ENGINE = "duckduckgo"
    MAX_SEARCH_RESULTS = 5
    SEARCH_TIMEOUT = 10
    FETCH_TIMEOUT = 15
    MAX_CONTENT_LENGTH = 10000
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(self):
        """Initialize configuration and create directories"""
        self.create_directories()
        self.load_config_file()

    def _safe_print(self, message):
        """Print helper that tolerates non-UTF8 terminals"""
        try:
            print(message)
        except UnicodeEncodeError:
            print(message.encode("ascii", errors="ignore").decode("ascii"))
    
    def create_directories(self):
        """Create all necessary directories"""
        directories = [
            self.CHAT_HISTORY_DIR,
            self.CONTEXT_FILES_DIR,
            self.UPLOADS_DIR,
            self.DOWNLOADS_DIR,
            self.LOGS_DIR,
            self.CACHE_DIR,
            self.TEMP_DIR,
            self.OFFLOAD_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_config_file(self):
        """Load configuration from YAML file if it exists"""
        config_file = self.BASE_DIR / "system_config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                
                # Override defaults with user config
                if user_config:
                    self._apply_user_config(user_config)
                    self._safe_print("✓ Loaded custom configuration from system_config.yaml")
            except Exception as e:
                self._safe_print(f"⚠ Could not load config file: {e}")
                self._safe_print("Using default configuration")
    
    def _apply_user_config(self, user_config):
        """Apply user configuration from YAML"""
        
        # Model settings
        if 'model' in user_config:
            model = user_config['model']
            if 'name' in model:
                self.MODEL_NAME = model['name']
            
            if 'quantization' in model:
                quant = model['quantization']
                self.QUANTIZATION_BITS = quant.get('bits', self.QUANTIZATION_BITS)
                self.QUANTIZATION_TYPE = quant.get('type', self.QUANTIZATION_TYPE)
            
            if 'context' in model:
                ctx = model['context']
                self.MAX_CONTEXT_LENGTH = ctx.get('max_length', self.MAX_CONTEXT_LENGTH)
                self.DEFAULT_CONTEXT_LENGTH = ctx.get('default_length', self.DEFAULT_CONTEXT_LENGTH)
            
            if 'memory' in model:
                mem = model['memory']
                self.GPU_MAX_MEMORY = mem.get('gpu_max', self.GPU_MAX_MEMORY)
                self.CPU_MAX_MEMORY = mem.get('cpu_max', self.CPU_MAX_MEMORY)
                self.DISK_MAX_MEMORY = mem.get('disk_max', self.DISK_MAX_MEMORY)
            
            if 'generation' in model:
                gen = model['generation']
                self.DEFAULT_TEMPERATURE = gen.get('temperature', self.DEFAULT_TEMPERATURE)
                self.DEFAULT_TOP_P = gen.get('top_p', self.DEFAULT_TOP_P)
                self.DEFAULT_TOP_K = gen.get('top_k', self.DEFAULT_TOP_K)
                self.DEFAULT_MAX_TOKENS = gen.get('max_new_tokens', self.DEFAULT_MAX_TOKENS)
        
        # Audio settings
        if 'audio' in user_config:
            audio = user_config['audio']
            self.TTS_ENGINE = audio.get('tts_engine', self.TTS_ENGINE)
            self.STT_ENGINE = audio.get('stt_engine', self.STT_ENGINE)
            
            if 'edge' in audio:
                edge = audio['edge']
                self.EDGE_VOICE = edge.get('voice', self.EDGE_VOICE)
                self.EDGE_RATE = edge.get('rate', self.EDGE_RATE)
                self.EDGE_VOLUME = edge.get('volume', self.EDGE_VOLUME)
            
            if 'whisper' in audio:
                whisper = audio['whisper']
                self.WHISPER_MODEL_SIZE = whisper.get('model_size', self.WHISPER_MODEL_SIZE)
                self.WHISPER_DEVICE = whisper.get('device', self.WHISPER_DEVICE)
        
        # Memory settings
        if 'memory' in user_config:
            mem = user_config['memory']
            self.MAX_MESSAGES_IN_MEMORY = mem.get('max_messages_in_memory', self.MAX_MESSAGES_IN_MEMORY)
            self.AUTO_SAVE_INTERVAL = mem.get('auto_save_interval', self.AUTO_SAVE_INTERVAL)
            self.MAX_CONTEXT_FILES = mem.get('max_context_files', self.MAX_CONTEXT_FILES)

        # Internet settings
        if 'internet' in user_config:
            internet = user_config['internet']
            self.SEARCH_ENGINE = internet.get('search_engine', self.SEARCH_ENGINE)
            self.MAX_SEARCH_RESULTS = internet.get('max_search_results', self.MAX_SEARCH_RESULTS)
            self.SEARCH_TIMEOUT = internet.get('search_timeout', self.SEARCH_TIMEOUT)
            self.FETCH_TIMEOUT = internet.get('fetch_timeout', self.FETCH_TIMEOUT)
            self.MAX_CONTENT_LENGTH = internet.get('max_content_length', self.MAX_CONTENT_LENGTH)
            self.USER_AGENT = internet.get('user_agent', self.USER_AGENT)
        
        # UI settings
        if 'ui' in user_config:
            ui = user_config['ui']
            self.UI_PORT = ui.get('port', self.UI_PORT)
            self.UI_SERVER = ui.get('server_name', self.UI_SERVER)
            self.UI_SHARE = ui.get('share', self.UI_SHARE)
            self.UI_THEME = ui.get('theme', self.UI_THEME)
    
    def get_personality_defaults(self):
        """Get default personality parameters"""
        return {
            "system_prompt": "You are a helpful AI assistant.",
            "temperature": self.DEFAULT_TEMPERATURE,
            "top_p": self.DEFAULT_TOP_P,
            "top_k": self.DEFAULT_TOP_K,
            "repetition_penalty": self.DEFAULT_REPETITION_PENALTY,
            "max_tokens": self.DEFAULT_MAX_TOKENS,
            "context_window": self.DEFAULT_CONTEXT_LENGTH
        }
    
    def save_config_template(self):
        """Save a template configuration file"""
        template_path = self.BASE_DIR / "system_config.yaml.template"
        
        if not template_path.exists():
            # The template is already in system_config.yaml artifact
            print("Template already exists as system_config.yaml")

# Global configuration instance
config = Config()
