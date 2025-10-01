"""
Model Manager Module - ULTIMATE FIX
Avoids padding completely to prevent CUDA assertion errors
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
from threading import Thread
from config import config

class ModelManager:
    """Manages the LLM with NO PADDING to avoid CUDA errors"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
    
    def load_model(self):
        """Load model with 4-bit quantization"""
        print(f"Loading model: {config.MODEL_NAME}")
        print(f"Target device: {self.device}")
        
        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        
        print("Configuring 4-bit quantization...")
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        
        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.MODEL_NAME,
            trust_remote_code=True
        )
        
        # CRITICAL: Set padding to right side and use eos_token
        self.tokenizer.padding_side = "left"  # Changed to left for decoder models
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        
        print("Loading model (this will take 3-5 minutes)...")
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                config.MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            self.model.eval()
            self.model_loaded = True
            
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / 1e9
                print(f"\nModel loaded successfully!")
                print(f"GPU Memory: {allocated:.2f}GB")
            
        except Exception as e:
            print(f"\nError loading model: {e}")
            print("\nTrying fallback loading strategy...")
            
            try:
                torch.cuda.empty_cache()
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    config.MODEL_NAME,
                    quantization_config=quantization_config,
                    device_map={"": 0},
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True
                )
                
                self.model.eval()
                self.model_loaded = True
                
                if torch.cuda.is_available():
                    allocated = torch.cuda.memory_allocated(0) / 1e9
                    print(f"\nModel loaded successfully (fallback method)!")
                    print(f"GPU Memory: {allocated:.2f}GB")
                
            except Exception as e2:
                print(f"\nFallback also failed: {e2}")
                raise
    
    def generate_response_stream(self, messages, personality_params, context_window=None):
        """Generate response with token streaming - NO PADDING VERSION"""
        if not self.model_loaded:
            yield "Model not loaded yet. Please wait..."
            return
        
        if context_window is None:
            context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Format messages
        prompt = self._format_messages(messages, personality_params, context_window)
        
        # CRITICAL FIX: NO PADDING - just encode normally
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=context_window,
            add_special_tokens=True
        )
        
        # Move to device
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)
        
        # Calculate max new tokens
        prompt_length = input_ids.shape[1]
        max_new_tokens = min(
            personality_params.get("max_tokens", 1024),
            context_window - prompt_length - 50
        )
        
        if max_new_tokens < 10:
            yield "Error: Context is full. Please clear chat or reduce context window."
            return
        
        # Create streamer
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        # Generation kwargs - SIMPLIFIED
        generation_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "max_new_tokens": max_new_tokens,
            "temperature": max(0.1, personality_params.get("temperature", 0.7)),  # Avoid 0
            "top_p": personality_params.get("top_p", 0.9),
            "top_k": personality_params.get("top_k", 50),
            "repetition_penalty": personality_params.get("repetition_penalty", 1.1),
            "do_sample": True,
            "eos_token_id": self.tokenizer.eos_token_id,
            "pad_token_id": self.tokenizer.eos_token_id,  # Use eos as pad
            "streamer": streamer,
            "use_cache": True
        }
        
        # Start generation in thread
        generation_thread = Thread(
            target=self._generate_with_streamer,
            kwargs=generation_kwargs
        )
        generation_thread.start()
        
        # Yield tokens
        try:
            for token in streamer:
                yield token
        except Exception as e:
            yield f"\n\nError during generation: {e}"
        
        # Wait for completion
        generation_thread.join()
        
        # Safe cache clearing
        try:
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
        except:
            pass
    
    def generate_response(self, messages, personality_params, context_window=None):
        """Non-streaming generation - NO PADDING VERSION"""
        if not self.model_loaded:
            return "Model not loaded yet. Please wait..."
        
        if context_window is None:
            context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Format messages
        prompt = self._format_messages(messages, personality_params, context_window)
        
        # NO PADDING - just encode
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=context_window,
            add_special_tokens=True
        )
        
        # Move to device
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)
        
        # Calculate max tokens
        prompt_length = input_ids.shape[1]
        max_new_tokens = min(
            personality_params.get("max_tokens", 1024),
            context_window - prompt_length - 50
        )
        
        print(f"Generating (prompt: {prompt_length} tokens, max new: {max_new_tokens})...")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                temperature=max(0.1, personality_params.get("temperature", 0.7)),
                top_p=personality_params.get("top_p", 0.9),
                top_k=personality_params.get("top_k", 50),
                repetition_penalty=personality_params.get("repetition_penalty", 1.1),
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()
        
        # Safe cache clearing
        try:
            if torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
        except:
            pass
        
        return response
    
    def _format_messages(self, messages, personality_params, context_window):
        """Format messages into prompt string"""
        system_prompt = personality_params.get("system_prompt", "You are a helpful AI assistant.")
        
        # Calculate available space
        available_tokens = context_window - personality_params.get("max_tokens", 1024) - 200
        available_chars = available_tokens * 4
        
        # Start with system prompt
        formatted = f"{system_prompt}\n\n"
        current_length = len(formatted)
        
        # Add messages from most recent backwards
        included_messages = []
        for msg in reversed(messages):
            msg_text = f"{msg['role'].capitalize()}: {msg['content']}\n\n"
            if current_length + len(msg_text) < available_chars:
                included_messages.insert(0, msg_text)
                current_length += len(msg_text)
            else:
                break
        
        formatted += "".join(included_messages)
        formatted += "Assistant:"
        
        return formatted
    
    def _generate_with_streamer(self, **kwargs):
        """Run generation with error handling"""
        try:
            self.model.generate(**kwargs)
        except Exception as e:
            print(f"Generation error: {e}")
            streamer = kwargs.get("streamer")
            if streamer:
                try:
                    streamer.end()
                except:
                    pass
    
    def get_model_info(self):
        """Get model information"""
        if not self.model_loaded:
            return {
                "loaded": False,
                "name": config.MODEL_NAME,
                "device": self.device
            }
        
        info = {
            "loaded": True,
            "name": config.MODEL_NAME,
            "device": self.device,
            "quantization": "4-bit NF4"
        }
        
        if torch.cuda.is_available():
            info["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1e9:.2f}GB"
            info["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1e9:.2f}GB"
        
        return info
    
    def unload_model(self):
        """Unload model from memory"""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        self.model_loaded = False
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print("Model unloaded from memory")

# Global model manager instance
model_manager = ModelManager()
