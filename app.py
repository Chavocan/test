"""
Local LLM Interface - Fixed Version
- TRUE token streaming with proper UI updates
- All imports working correctly
- Cleaner regenerate function
- Better context preview
"""

import gradio as gr
import threading
from datetime import datetime

# Import all modules (now all exist)
from config import config
from model_manager import model_manager
from chat_manager import chat_manager
from context_manager import context_manager
from personality import personality_system
from audio_handler import voice_handler
from screen_handler import screen_handler
from internet_handler import internet_handler

# Global state
model_loading_status = {"status": "initializing", "progress": 0}
last_response_data = {"content": "", "params": None, "messages": None, "user_message": None}

def initialize_model():
    """Load model with progress updates"""
    global model_loading_status
    try:
        model_loading_status = {"status": "loading", "progress": 50}
        model_manager.load_model()
        model_loading_status = {"status": "ready", "progress": 100}
    except Exception as e:
        model_loading_status = {"status": "error", "progress": 0}
        print(f"Error loading model: {e}")

def chat_function_streaming(message, history, system_prompt, temperature, max_tokens,
                            top_p, top_k, repetition_penalty, context_window,
                            selected_context_files):
    """
    Main chat function with TRUE streaming
    Yields partial responses as tokens are generated
    """
    global last_response_data
    
    if not message.strip():
        yield history, ""
        return
    
    # Build personality params
    personality_params = {
        "system_prompt": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "repetition_penalty": repetition_penalty,
        "context_window": context_window
    }
    
    # Check context limit
    warning_msg, auto_file = chat_manager.check_context_limit(personality_params)
    
    # Add user message
    chat_manager.add_message("user", message)
    
    # Get context from files
    context_content = ""
    if selected_context_files:
        context_content = context_manager.get_context_files_content(
            selected_context_files,
            max_tokens=config.CONTEXT_TOKEN_BUDGET
        )
    
    # Get messages
    messages = chat_manager.get_messages()
    
    # Add context warning prefix if needed
    prefix = ""
    if warning_msg:
        prefix = warning_msg + "\n\n---\n\n"
        if auto_file:
            if "context_files" not in chat_manager.current_session:
                chat_manager.current_session["context_files"] = []
            chat_manager.current_session["context_files"].append(auto_file)
    
    # Initialize streaming response
    full_response = prefix
    history.append((message, ""))
    
    # Stream tokens - THIS IS THE CRITICAL FIX
    for token in model_manager.generate_response_stream(messages, personality_params, context_window):
        full_response += token
        # Update the last message's assistant response
        history[-1] = (message, full_response)
        yield history, ""  # Yield updated history to Gradio
    
    # Store for regenerate
    last_response_data = {
        "content": full_response,
        "params": personality_params,
        "messages": messages,
        "user_message": message
    }
    
    # Add to chat manager
    chat_manager.add_message("assistant", full_response)
    
    yield history, ""

def regenerate_last(history, system_prompt, temperature, max_tokens,
                   top_p, top_k, repetition_penalty, context_window,
                   selected_context_files):
    """Regenerate the last response - FIXED"""
    if not last_response_data.get("user_message") or not history:
        yield history
        return
    
    # Remove last assistant message from history and chat manager
    if history:
        last_user_msg = history[-1][0]
        history = history[:-1]
    
    if chat_manager.current_session and chat_manager.current_session["messages"]:
        # Remove last assistant message
        if chat_manager.current_session["messages"][-1]["role"] == "assistant":
            chat_manager.current_session["messages"].pop()
    
    # Regenerate using the streaming function
    personality_params = {
        "system_prompt": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "top_k": top_k,
        "repetition_penalty": repetition_penalty,
        "context_window": context_window
    }
    
    # Get fresh messages
    messages = chat_manager.get_messages()
    
    # Initialize new response
    full_response = ""
    history.append((last_user_msg, ""))
    
    # Stream new response
    for token in model_manager.generate_response_stream(messages, personality_params, context_window):
        full_response += token
        history[-1] = (last_user_msg, full_response)
        yield history
    
    # Update chat manager
    chat_manager.add_message("assistant", full_response)
    
    # Update stored data
    last_response_data["content"] = full_response
    
    yield history

def estimate_tokens(text):
    """Quick token estimation"""
    return len(text) // 4

def update_token_display(message):
    """Update token counter"""
    tokens = estimate_tokens(message)
    total = config.DEFAULT_CONTEXT_LENGTH
    pct = (tokens / total) * 100
    return f"📝 {tokens:,} tokens ({pct:.1f}%)"

def get_context_usage():
    """Get current context usage"""
    if not chat_manager.current_session:
        return "0/16,384 (0.0%)"
    
    personality_params = config.get_personality_defaults()
    used, total, pct, _, _ = chat_manager.estimate_context_usage(personality_params)
    
    # Color coding with emojis
    if pct < 0.7:
        emoji = "🟢"
    elif pct < 0.9:
        emoji = "🟡"
    else:
        emoji = "🔴"
    
    return f"{emoji} {used:,}/{total:,} ({pct*100:.0f}%)"

def show_context_preview(files):
    """Show preview of selected files - IMPROVED"""
    if not files:
        return "*Select files to preview*"
    
    previews = []
    for f in files[:3]:  # Show first 3
        content = context_manager.load_context_file(f)
        if content:
            # Increased preview length to 400 chars
            preview = content[:400].replace('\n', ' ')
            if len(content) > 400:
                preview += "..."
            previews.append(f"**{f}:**\n{preview}\n")
    
    if len(files) > 3:
        previews.append(f"*...and {len(files)-3} more files*")
    
    return "\n".join(previews) if previews else "*No preview available*"

def new_session():
    """Create new session"""
    session_id = chat_manager.create_session()
    return [], f"✅ New session: {session_id}", get_context_usage()

def load_preset(preset_name):
    """Load personality preset"""
    preset = personality_system.get_preset(preset_name)
    dims = preset["dimensions"]
    prompt = personality_system.build_system_prompt(dims)
    
    return (
        prompt,
        dims.get("temperature", 70) / 100,
        gr.update(), gr.update(), gr.update(), gr.update()
    )

def voice_input_handler(audio_file):
    """Process voice input"""
    if not audio_file:
        return ""
    
    transcription = voice_handler.speech_to_text(audio_file)
    return transcription

def voice_output_handler(history):
    """Generate voice output from last response"""
    if not history or not history[-1][1]:
        return None
    
    last_response = history[-1][1]
    audio_file = voice_handler.text_to_speech(last_response)
    return audio_file

def create_context_file_handler(name, content, category):
    """Create new context file"""
    if not name or not content:
        return "⚠️ Name and content required", gr.update()
    
    filepath = context_manager.create_context_file(content, name, category)
    if filepath:
        files = context_manager.list_context_files()
        file_names = [f["name"] for f in files]
        return f"✅ Created: {name}", gr.update(choices=file_names)
    else:
        return "❌ Failed to create file", gr.update()

def refresh_context_files():
    """Refresh context files list"""
    files = context_manager.list_context_files()
    file_names = [f["name"] for f in files]
    return gr.update(choices=file_names)

def web_search_handler(query):
    """Search the web"""
    if not query:
        return "⚠️ Enter search query"
    
    results = internet_handler.search_web(query)
    
    if not results:
        return "No results found"
    
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"{i}. **{result['title']}**")
        formatted.append(f"   {result['url']}")
        formatted.append(f"   {result['snippet']}\n")
    
    return "\n".join(formatted)

def fetch_url_handler(url):
    """Fetch content from URL"""
    if not url:
        return "⚠️ Enter URL"
    
    content = internet_handler.fetch_url(url)
    return content

def capture_screen_handler():
    """Capture screenshot"""
    screenshot_path = screen_handler.capture_screen()
    if screenshot_path:
        return screenshot_path, "✅ Screenshot captured"
    else:
        return None, "❌ Failed to capture"

def screen_action_handler(action_type, x, y, text):
    """Execute screen action"""
    try:
        if action_type == "click":
            if x is None or y is None:
                return "⚠️ X and Y coordinates required"
            result = screen_handler.click(int(x), int(y))
        
        elif action_type == "type":
            if not text:
                return "⚠️ Text required"
            result = screen_handler.type_text(text)
        
        elif action_type == "move":
            if x is None or y is None:
                return "⚠️ X and Y coordinates required"
            result = screen_handler.move_mouse(int(x), int(y))
        
        else:
            result = "❌ Unknown action"
        
        return result
    except Exception as e:
        return f"❌ Error: {e}"

# Build interface
def create_interface():
    """Create the dark-themed streaming interface"""
    
    # Custom CSS
    custom_css = """
    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #16181d;
        --bg-tertiary: #1c1f26;
        --text-primary: #e8eaed;
        --text-secondary: #9aa0a6;
        --accent: #8ab4f8;
        --border: #2d3139;
    }
    
    body { background: var(--bg-primary) !important; color: var(--text-primary) !important; }
    .gradio-container { background: var(--bg-primary) !important; }
    textarea, input { background: var(--bg-secondary) !important; color: var(--text-primary) !important; 
                      border: 1px solid var(--border) !important; }
    .token-counter { font-size: 0.9em; color: var(--text-secondary); text-align: right; }
    """
    
    with gr.Blocks(theme=gr.themes.Base(), css=custom_css, title="LLM Interface") as app:
        # Header
        gr.Markdown("# 🌙 Local LLM Interface")
        gr.Markdown("*Streaming • Dark Theme • 16K Context*")
        
        with gr.Tab("💬 Chat"):
            with gr.Row():
                # Main chat area
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        height=550,
                        show_label=False,
                        type="tuples"
                    )
                    
                    token_counter = gr.Markdown(
                        "0 tokens (0.0%)",
                        elem_classes="token-counter"
                    )
                    
                    msg_input = gr.Textbox(
                        label="",
                        placeholder="Type your message... (Shift+Enter for new line)",
                        lines=3,
                        show_label=False
                    )
                    
                    with gr.Row():
                        send_btn = gr.Button("Send 📤", variant="primary", scale=3)
                        regen_btn = gr.Button("↻ Regenerate", scale=1)
                        clear_btn = gr.Button("Clear", scale=1)
                    
                    # Voice (collapsed)
                    with gr.Accordion("🎤 Voice", open=False):
                        with gr.Row():
                            audio_input = gr.Audio(sources=["microphone"], type="filepath")
                            voice_btn = gr.Button("Transcribe")
                        voice_out_btn = gr.Button("🔊 Read Last Response")
                        audio_output = gr.Audio(label="Output", visible=True)
                
                # Sidebar
                with gr.Column(scale=1):
                    # Context usage
                    context_display = gr.Textbox(
                        value=get_context_usage(),
                        label="Context",
                        interactive=False,
                        lines=1
                    )
                    
                    # Settings
                    with gr.Accordion("⚙️ Settings", open=False):
                        preset_dropdown = gr.Dropdown(
                            choices=[p["id"] for p in personality_system.list_presets()],
                            label="Preset",
                            value="default"
                        )
                        
                        system_prompt = gr.Textbox(
                            label="System Prompt",
                            value="You are a helpful AI assistant.",
                            lines=2
                        )
                        
                        temperature = gr.Slider(0.1, 2.0, value=0.7, step=0.1, label="Temperature")
                        max_tokens = gr.Slider(128, 4096, value=1024, step=128, label="Max Tokens")
                        context_window = gr.Slider(4096, 16384, value=12288, step=2048, label="Context")
                        top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top P")
                        top_k = gr.Slider(1, 100, value=50, step=1, label="Top K")
                        repetition_penalty = gr.Slider(1.0, 2.0, value=1.1, step=0.1, label="Rep. Penalty")
                    
                    # Context files
                    with gr.Accordion("📁 Context", open=False):
                        files = context_manager.list_context_files()
                        file_names = [f["name"] for f in files]
                        
                        selected_files = gr.CheckboxGroup(
                            choices=file_names,
                            label="",
                            show_label=False
                        )
                        
                        preview_box = gr.Markdown(
                            "*Select files for preview*"
                        )
                        
                        gr.Button("🔄 Refresh", size="sm")
                    
                    # Session
                    with gr.Accordion("💾 Session", open=False):
                        new_sess_btn = gr.Button("New")
                        save_sess_btn = gr.Button("Save")
                        sess_status = gr.Textbox(label="", show_label=False, lines=1, interactive=False)
        
        with gr.Tab("📁 Files"):
            gr.Markdown("### Context File Manager")
            with gr.Row():
                with gr.Column():
                    ctx_name = gr.Textbox(label="Name", placeholder="notes.txt")
                    ctx_category = gr.Dropdown(
                        choices=context_manager.list_categories(),
                        label="Category",
                        allow_custom_value=True
                    )
                    ctx_content = gr.Textbox(label="Content", lines=15)
                    ctx_save_btn = gr.Button("💾 Save", variant="primary")
                    ctx_status = gr.Textbox(label="Status", interactive=False)
        
        with gr.Tab("🌐 Web"):
            gr.Markdown("### Internet Access")
            with gr.Row():
                with gr.Column():
                    search_query = gr.Textbox(label="Search")
                    search_btn = gr.Button("🔍 Search", variant="primary")
                    search_results = gr.Textbox(label="Results", lines=15, interactive=False)
                
                with gr.Column():
                    url_input = gr.Textbox(label="URL")
                    fetch_btn = gr.Button("📥 Fetch", variant="primary")
                    url_content = gr.Textbox(label="Content", lines=15, interactive=False)
        
        with gr.Tab("🖥️ Screen"):
            gr.Markdown("### Screen Control")
            with gr.Row():
                with gr.Column():
                    capture_btn = gr.Button("📸 Capture", variant="primary")
                    screen_img = gr.Image(label="Screenshot", type="filepath")
                    screen_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    action_type = gr.Dropdown(["click", "type", "move"], label="Action", value="click")
                    action_x = gr.Number(label="X", value=500)
                    action_y = gr.Number(label="Y", value=500)
                    action_text = gr.Textbox(label="Text (for typing)")
                    execute_btn = gr.Button("⚡ Execute")
                    action_result = gr.Textbox(label="Result", interactive=False)
        
        # Event handlers
        
        # Token counter
        msg_input.change(
            update_token_display,
            inputs=[msg_input],
            outputs=[token_counter]
        )
        
        # Context preview
        selected_files.change(
            show_context_preview,
            inputs=[selected_files],
            outputs=[preview_box]
        )
        
        # Main chat with streaming
        send_btn.click(
            chat_function_streaming,
            inputs=[msg_input, chatbot, system_prompt, temperature, max_tokens,
                    top_p, top_k, repetition_penalty, context_window, selected_files],
            outputs=[chatbot, msg_input]
        ).then(
            lambda: get_context_usage(),
            outputs=[context_display]
        )
        
        msg_input.submit(
            chat_function_streaming,
            inputs=[msg_input, chatbot, system_prompt, temperature, max_tokens,
                    top_p, top_k, repetition_penalty, context_window, selected_files],
            outputs=[chatbot, msg_input]
        ).then(
            lambda: get_context_usage(),
            outputs=[context_display]
        )
        
        # Regenerate
        regen_btn.click(
            regenerate_last,
            inputs=[chatbot, system_prompt, temperature, max_tokens, top_p, top_k,
                    repetition_penalty, context_window, selected_files],
            outputs=[chatbot]
        ).then(
            lambda: get_context_usage(),
            outputs=[context_display]
        )
        
        # Clear
        clear_btn.click(
            lambda: ([], ""),
            outputs=[chatbot, msg_input]
        ).then(
            lambda: get_context_usage(),
            outputs=[context_display]
        )
        
        # Voice
        voice_btn.click(voice_input_handler, inputs=[audio_input], outputs=[msg_input])
        voice_out_btn.click(voice_output_handler, inputs=[chatbot], outputs=[audio_output])
        
        # Preset
        preset_dropdown.change(
            load_preset,
            inputs=[preset_dropdown],
            outputs=[system_prompt, temperature, gr.State(), gr.State(), gr.State(), gr.State()]
        )
        
        # Context files
        ctx_save_btn.click(
            create_context_file_handler,
            inputs=[ctx_name, ctx_content, ctx_category],
            outputs=[ctx_status, selected_files]
        )
        
        # Session
        new_sess_btn.click(new_session, outputs=[chatbot, sess_status, context_display])
        save_sess_btn.click(
            lambda: "✅ Saved" if chat_manager.save_session() else "❌ Failed",
            outputs=[sess_status]
        )
        
        # Screen
        capture_btn.click(capture_screen_handler, outputs=[screen_img, screen_status])
        execute_btn.click(
            screen_action_handler,
            inputs=[action_type, action_x, action_y, action_text],
            outputs=[action_result]
        )
        
        # Internet
        search_btn.click(web_search_handler, inputs=[search_query], outputs=[search_results])
        fetch_btn.click(fetch_url_handler, inputs=[url_input], outputs=[url_content])
    
    return app

if __name__ == "__main__":
    print("=" * 60)
    print("Local LLM Interface - Fixed Version")
    print("=" * 60)
    print(f"Model: {config.MODEL_NAME}")
    print("Features:")
    print("  • TRUE token streaming (words appear as generated)")
    print("  • Fixed imports (all handlers working)")
    print("  • Better context preview (400 chars)")
    print("  • Improved regenerate function")
    print("=" * 60)
    
    # Load model in background
    print("\nLoading model in background...")
    model_thread = threading.Thread(target=initialize_model, daemon=True)
    model_thread.start()
    
    # Create session
    chat_manager.create_session()
    
    # Launch
    print("\nLaunching interface...")
    print("URL: http://127.0.0.1:7860")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    app = create_interface()
    app.launch(
        server_name=config.UI_SERVER,
        server_port=config.UI_PORT,
        share=config.UI_SHARE,
        show_error=True
    )
