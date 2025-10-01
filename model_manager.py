"""
Model Manager Module with TRUE Token Streaming
SIMPLIFIED loading to avoid meta tensor issues
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
from threading import Thread
from config import config

class ModelManager:
    """Manages the LLM with optimized loading and streaming generation"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.inference_device = torch.device("cuda:0") if self.device == "cuda" else torch.device("cpu")
        self.compute_dtype = self._resolve_compute_dtype()
        self.model_loaded = False
    
    def load_model(self):
        """Load model with 4-bit quantization - ROBUST approach"""
        print(f"Loading model: {config.MODEL_NAME}")
        print(f"Target device: {self.device}")
        
        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
            print(f"Compute dtype: {self.compute_dtype}")
        
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
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("Loading model (this will take 3-5 minutes)...")
        
        try:
            import accelerate
            print(f"Accelerate version: {accelerate.__version__}")
            
            # SIMPLIFIED: Let it auto-handle everything without max_memory restrictions
            self.model = AutoModelForCausalLM.from_pretrained(
                config.MODEL_NAME,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16
            )
            
            self.model.eval()
            self.model_loaded = True
            
            # Print memory stats
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated(0) / 1e9
                reserved = torch.cuda.memory_reserved(0) / 1e9
                print(f"\nModel loaded successfully!")
                print(f"GPU Memory - Allocated: {allocated:.2f}GB | Reserved: {reserved:.2f}GB")
            else:
                print("Model loaded successfully (CPU mode)")
            
        except Exception as e:
            print(f"\nError loading model: {e}")
            
            # Try fallback: force everything on GPU 0
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
                print("\nTROUBLESHOOTING:")
                print("The model may be too large even with 4-bit quantization.")
                print("\nOptions:")
                print("1. Close ALL GPU applications (Chrome, Discord, etc)")
                print("2. Restart computer")
                print("3. Try a smaller model: 'mlabonne/NeuralHermes-2.5-Mistral-7B'")
                raise
    
    def generate_response_stream(self, messages, personality_params, context_window=None):
        """
        Generate response with TRUE token-by-token streaming
        Yields each token as it's generated
        """
        if not self.model_loaded:
            yield "Model not loaded yet. Please wait..."
            return
        
        if context_window is None:
            context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Format messages into prompt
        prompt = self._format_messages(messages, personality_params, context_window)
        
        # Tokenize input and move tensors to the active device
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=context_window
        )

        inputs = self._move_inputs_to_device(inputs)
        
        # Calculate max new tokens
        prompt_length = inputs.input_ids.shape[1]
        max_new_tokens = min(
            personality_params.get("max_tokens", 1024),
            context_window - prompt_length - 50
        )
        
        if max_new_tokens < 10:
            yield "Error: Context is full. Please clear chat or reduce context window."
            return
        
        # Create streamer for token-by-token output
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        # Generation parameters
        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_new_tokens,
            "temperature": personality_params.get("temperature", 0.7),
            "top_p": personality_params.get("top_p", 0.9),
            "top_k": personality_params.get("top_k", 50),
            "repetition_penalty": personality_params.get("repetition_penalty", 1.1),
            "do_sample": True,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer,
            "use_cache": True
        }
        
        # Start generation in separate thread
        generation_thread = Thread(
            target=self._generate_with_streamer,
            kwargs=generation_kwargs
        )
        generation_thread.start()
        
        # Yield tokens as they're generated
        try:
            for token in streamer:
                yield token
        except Exception as e:
            yield f"\n\nError during generation: {e}"
        
        # Wait for generation to complete
        generation_thread.join()
        
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def generate_response(self, messages, personality_params, context_window=None):
        """
        Non-streaming generation (for compatibility)
        Returns complete response at once
        """
        if not self.model_loaded:
            return "Model not loaded yet. Please wait..."
        
        if context_window is None:
            context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Format messages
        prompt = self._format_messages(messages, personality_params, context_window)
        
        # Tokenize and move tensors to the active device
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=context_window
        )

        inputs = self._move_inputs_to_device(inputs)
        
        # Calculate max tokens
        prompt_length = inputs.input_ids.shape[1]
        max_new_tokens = min(
            personality_params.get("max_tokens", 1024),
            context_window - prompt_length - 50
        )
        
        print(f"Generating response (prompt: {prompt_length} tokens, max new: {max_new_tokens})...")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=personality_params.get("temperature", 0.7),
                top_p=personality_params.get("top_p", 0.9),
                top_k=personality_params.get("top_k", 50),
                repetition_penalty=personality_params.get("repetition_penalty", 1.1),
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(prompt):].strip()
        
        # Clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return response

    def _resolve_compute_dtype(self):
        """Determine the best compute dtype based on config and hardware"""
        requested = getattr(config, "COMPUTE_DTYPE", "float16").lower()
        if requested == "bfloat16":
            supports_bf16 = False
            if torch.cuda.is_available() and hasattr(torch.cuda, "is_bf16_supported"):
                supports_bf16 = torch.cuda.is_bf16_supported()
            if supports_bf16:
                return torch.bfloat16
            print("bfloat16 requested but not supported. Falling back to float16.")
        return torch.float16

    def _move_inputs_to_device(self, inputs):
        """Move tokenizer outputs to the active inference device"""
        if self.device == "cpu":
            return inputs

        # Prefer the device of the first parameter
        target_device = None
        try:
            first_param = next(self.model.parameters())
            target_device = first_param.device
        except StopIteration:
            target_device = torch.device(self.device)

        if hasattr(inputs, "to"):
            return inputs.to(target_device)

        return {
            key: value.to(target_device) if torch.is_tensor(value) else value
            for key, value in inputs.items()
        }
    
    def _format_messages(self, messages, personality_params, context_window):
        """Format messages into a prompt string"""
        system_prompt = personality_params.get("system_prompt", "You are a helpful AI assistant.")
        
        # Calculate available space
        available_tokens = context_window - personality_params.get("max_tokens", 1024) - 200
        available_chars = available_tokens * 4
        
        # Start with system prompt
        formatted = f"System: {system_prompt}\n\n"
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
        formatted += "Assistant: "
        
        return formatted
    
    def get_model_info(self):
        """Get information about the loaded model"""
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
        """Unload model to free memory"""
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

    def _generate_with_streamer(self, **kwargs):
        """Run model.generate and push exceptions through the streamer"""
        streamer = kwargs.get("streamer")
        try:
            self.model.generate(**kwargs)
        except Exception as exc:
            if streamer is not None:
                try:
                    streamer.put(f"\n\nError during generation: {exc}")
                except Exception:
                    pass
                try:
                    streamer.end()
                except Exception:
                    pass

# Global model manager instance
model_manager = ModelManager()