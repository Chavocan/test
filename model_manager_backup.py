"""
Model Manager Module
Handles model loading, optimization, and text generation
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import config

class ModelManager:
    """Manages the LLM model lifecycle and generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        
    def load_model(self):
        """Load and optimize the model for RTX 4080"""
        if self.is_loaded:
            print("Model already loaded!")
            return
        
        print(f"Loading model on {self.device}...")
        print(f"Optimizing for RTX 4080 (16GB VRAM)...")
        print(f"Using {config.QUANTIZATION_BITS}-bit quantization...")
        
        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        
        # Configure quantization for 16GB GPU
        quantization_config = None
        if self.device == "cuda":
            from transformers import BitsAndBytesConfig
            
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=config.USE_DOUBLE_QUANT,
                bnb_4bit_quant_type=config.QUANTIZATION_TYPE
            )
        
        # Load model with optimizations
        print("Loading model (this may take a few minutes)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            config.MODEL_NAME,
            quantization_config=quantization_config,
            device_map="auto",
            max_memory={0: config.GPU_MAX_MEMORY, "cpu": config.CPU_MAX_MEMORY},
            offload_folder=str(config.OFFLOAD_DIR),
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        
        # Enable memory-efficient attention if available
        try:
            from optimum.bettertransformer import BetterTransformer
            self.model = BetterTransformer.transform(self.model)
            print("✓ Memory-efficient attention enabled!")
        except Exception as e:
            print(f"⚠ Standard attention (install optimum for better memory)")
        
        self.is_loaded = True
        
        # Print memory usage
        if self.device == "cuda":
            memory_used = torch.cuda.memory_allocated(0) / 1e9
            print(f"✓ Model loaded successfully!")
            print(f"✓ GPU Memory usage: ~{memory_used:.2f}GB")
        else:
            print(f"✓ Model loaded on CPU")
    
    def generate_response(self, messages, personality_params, context_window=None):
        """Generate a response from the model"""
        if not self.is_loaded:
            return "⚠ Model not loaded. Please wait for initialization..."
        
        # Use provided context window or default
        if context_window is None:
            context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Format messages into prompt
        prompt = self._format_messages(messages, personality_params, context_window)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=context_window
        ).to(self.device)
        
        # Calculate available tokens for generation
        prompt_tokens = inputs.input_ids.shape[1]
        max_new_tokens = min(
            personality_params.get("max_tokens", config.DEFAULT_MAX_TOKENS),
            context_window - prompt_tokens - 50  # Safety buffer
        )
        
        if max_new_tokens < 50:
            return "⚠ Context is too long. Please reduce context or increase context window."
        
        # Generate
        print(f"Generating (prompt: {prompt_tokens} tokens, max new: {max_new_tokens} tokens)...")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=personality_params.get("temperature", config.DEFAULT_TEMPERATURE),
                top_p=personality_params.get("top_p", config.DEFAULT_TOP_P),
                top_k=personality_params.get("top_k", config.DEFAULT_TOP_K),
                repetition_penalty=personality_params.get("repetition_penalty", config.DEFAULT_REPETITION_PENALTY),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=True  # Important for long context
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only new generated text
        response = response[len(prompt):].strip()
        
        # Clear CUDA cache periodically to prevent memory buildup
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print(f"✓ Generated {len(response.split())} words")
        return response
    
    def _format_messages(self, messages, personality_params, context_window):
        """Format messages into a prompt string with smart truncation"""
        system_prompt = personality_params.get("system_prompt", "You are a helpful AI assistant.")
        
        # Calculate token budget for context (rough estimation: 4 chars ≈ 1 token)
        available_tokens = context_window - config.RESERVE_FOR_RESPONSE
        available_chars = available_tokens * 4
        
        # Start with system prompt
        formatted = f"System: {system_prompt}\n\n"
        current_length = len(formatted)
        
        # Add messages from most recent, working backwards
        included_messages = []
        for msg in reversed(messages):
            role = msg["role"].capitalize()
            msg_text = f"{role}: {msg['content']}\n\n"
            
            if current_length + len(msg_text) < available_chars:
                included_messages.insert(0, msg_text)
                current_length += len(msg_text)
            else:
                # Can't fit more messages
                break
        
        formatted += "".join(included_messages)
        formatted += "Assistant: "
        
        return formatted
    
    def estimate_tokens(self, text):
        """Estimate token count for a text string"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Rough estimation if tokenizer not loaded
            return len(text) // 4
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {
                "loaded": False,
                "device": self.device,
                "model_name": config.MODEL_NAME
            }
        
        info = {
            "loaded": True,
            "device": self.device,
            "model_name": config.MODEL_NAME,
            "quantization": f"{config.QUANTIZATION_BITS}-bit"
        }
        
        if self.device == "cuda" and torch.cuda.is_available():
            info["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1e9:.2f}GB"
            info["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1e9:.2f}GB"
            info["gpu_name"] = torch.cuda.get_device_name(0)
        
        return info
    
    def unload_model(self):
        """Unload model from memory"""
        if self.model:
            del self.model
            self.model = None
        
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_loaded = False
        print("✓ Model unloaded from memory")

# Global model manager instance
model_manager = ModelManager()
