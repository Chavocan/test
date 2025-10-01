"""
Chat Manager Module
Handles chat history, session management, and memory extraction
WITH automatic context monitoring and smart context file creation
"""

import json
import os
from datetime import datetime
from pathlib import Path
from config import config

class ChatHistoryManager:
    """Manages chat sessions and conversation history with memory extraction"""
    
    def __init__(self):
        self.current_session = None
        self.message_count = 0
        self.context_warning_shown = False
        self.auto_context_threshold = 0.80  # Warn at 80% full
        self.auto_context_create_threshold = 0.90  # Auto-create at 90% full
        
        # Memory extraction keywords
        self.memory_keywords = [
            "my name is",
            "i like",
            "i prefer",
            "i hate",
            "i dislike",
            "remember that",
            "important:",
            "note:",
            "keep in mind",
            "always",
            "never",
            "i am",
            "i work",
            "i use"
        ]
    
    def estimate_context_usage(self, personality_params):
        """
        Estimate how much of the context window is being used
        Returns: (used_tokens, total_tokens, percentage, should_warn, should_auto_create)
        """
        if not self.current_session:
            return (0, 0, 0.0, False, False)
        
        context_window = personality_params.get("context_window", config.DEFAULT_CONTEXT_LENGTH)
        
        # Estimate tokens (rough: 4 chars = 1 token)
        system_prompt = personality_params.get("system_prompt", "")
        system_tokens = len(system_prompt) // 4
        
        # Count message tokens
        message_tokens = 0
        for msg in self.current_session["messages"]:
            message_tokens += len(msg["content"]) // 4 + 5  # +5 for role/formatting
        
        # Add context file estimate (if we track them)
        context_file_tokens = self.current_session.get("estimated_context_tokens", 0)
        
        used_tokens = system_tokens + message_tokens + context_file_tokens
        percentage = used_tokens / context_window
        
        should_warn = percentage >= self.auto_context_threshold and not self.context_warning_shown
        should_auto_create = percentage >= self.auto_context_create_threshold
        
        return (used_tokens, context_window, percentage, should_warn, should_auto_create)
    
    def check_context_limit(self, personality_params):
        """
        Check if context limit is approaching
        Returns: (warning_message, auto_context_file_name) or (None, None)
        """
        used, total, percentage, should_warn, should_auto_create = self.estimate_context_usage(personality_params)
        
        if should_auto_create:
            # Auto-create context file
            context_file_name = self._auto_create_context_file()
            
            warning_msg = (
                f"⚠️ **Context at {percentage*100:.0f}%** ({used:,}/{total:,} tokens)\n\n"
                f"📄 **Auto-created context file:** `{context_file_name}`\n\n"
                f"This file contains a summary of the conversation so far. "
                f"I've compressed the older messages to make room. "
                f"The summary is now available as a context file for future sessions!"
            )
            
            self.context_warning_shown = False  # Reset for next cycle
            return (warning_msg, context_file_name)
        
        elif should_warn:
            # Just warn
            self.context_warning_shown = True
            
            warning_msg = (
                f"⚠️ **Context filling up:** {percentage*100:.0f}% used ({used:,}/{total:,} tokens)\n\n"
                f"**Options:**\n"
                f"1. I can auto-create a context file soon (at 90%)\n"
                f"2. You can ask me to summarize now: 'Create context summary'\n"
                f"3. Continue - I'll manage automatically\n"
                f"4. Increase context window in settings\n\n"
                f"💡 At 90%, I'll automatically create a summary file to free up space."
            )
            
            return (warning_msg, None)
        
        return (None, None)
    
    def _auto_create_context_file(self):
        """
        Automatically create a context file from conversation
        Returns: filename
        """
        if not self.current_session:
            return None
        
        # Generate summary of conversation
        summary_parts = []
        summary_parts.append(f"# Auto-generated Context Summary")
        summary_parts.append(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary_parts.append(f"Session: {self.current_session['id']}\n")
        
        # Add important facts
        if self.current_session.get("important_facts"):
            summary_parts.append("## Key Information")
            for key, value in self.current_session["important_facts"].items():
                summary_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
            summary_parts.append("")
        
        # Add memory items
        if self.current_session.get("memory_items"):
            summary_parts.append("## Important Notes")
            for item in self.current_session["memory_items"]:
                summary_parts.append(f"- {item['content']}")
            summary_parts.append("")
        
        # Summarize conversation topics
        summary_parts.append("## Conversation Summary")
        
        # Group messages by topic (simple approach: every 10 messages)
        messages = self.current_session["messages"]
        chunk_size = 10
        
        for i in range(0, len(messages), chunk_size):
            chunk = messages[i:i+chunk_size]
            if chunk:
                # Get first user message in chunk as topic indicator
                user_msgs = [m for m in chunk if m["role"] == "user"]
                if user_msgs:
                    first_topic = user_msgs[0]["content"][:100]
                    summary_parts.append(f"\n### Messages {i+1}-{i+len(chunk)}")
                    summary_parts.append(f"Topic: {first_topic}...")
                    
                    # Add key points from this chunk
                    for msg in chunk:
                        if len(msg["content"]) > 200:  # Only substantial messages
                            preview = msg["content"][:150] + "..."
                            summary_parts.append(f"- ({msg['role']}) {preview}")
        
        summary_parts.append("\n---")
        summary_parts.append("*This summary was auto-generated to manage context window.*")
        
        summary_content = "\n".join(summary_parts)
        
        # Save context file
        filename = f"auto_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        from context_manager import context_manager
        filepath = context_manager.create_context_file(summary_content, filename, "auto_generated")
        
        # Clear older messages (keep last 20)
        if len(self.current_session["messages"]) > 20:
            kept_messages = self.current_session["messages"][-20:]
            self.current_session["messages"] = kept_messages
            self.context_warning_shown = False
            
            print(f"✓ Auto-created context file: {filename}")
            print(f"✓ Compressed conversation: kept last 20 messages")
        
        return filename
    
    def create_session(self, personality_params=None):
        """Create a new chat session"""
        if personality_params is None:
            personality_params = config.get_personality_defaults()
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "personality": personality_params,
            "messages": [],
            "context_files": [],
            "memory_items": [],
            "important_facts": {},
            "topics_discussed": [],
            "message_count": 0
        }
        
        self.message_count = 0
        print(f"✓ Created new session: {session_id}")
        return session_id
    
    def add_message(self, role, content):
        """Add a message to current session with auto-save"""
        if not self.current_session:
            self.create_session()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.current_session["messages"].append(message)
        self.current_session["last_updated"] = datetime.now().isoformat()
        self.current_session["message_count"] += 1
        self.message_count += 1
        
        # Extract memory from user messages
        if role == "user":
            self._extract_memory(content)
        
        # Auto-save at intervals
        if self.message_count % config.AUTO_SAVE_INTERVAL == 0:
            self.save_session()
            print(f"✓ Auto-saved session (message #{self.message_count})")
    
    def _extract_memory(self, content):
        """Extract important information from user messages"""
        content_lower = content.lower()
        
        for keyword in self.memory_keywords:
            if keyword in content_lower:
                memory_item = {
                    "content": content,
                    "keyword": keyword,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.current_session["memory_items"].append(memory_item)
                print(f"🧠 Extracted memory: '{keyword}' - {content[:50]}...")
                
                # Extract specific facts
                if keyword == "my name is":
                    try:
                        name = content_lower.split("my name is")[1].split()[0].strip(".,!?")
                        self.current_session["important_facts"]["user_name"] = name.title()
                    except:
                        pass
                
                break  # Only store once per message
    
    def get_messages(self, max_tokens=None):
        """Get messages within token budget"""
        if not self.current_session:
            return []
        
        messages = self.current_session["messages"]
        
        if max_tokens is None:
            return messages
        
        # Estimate tokens and return messages that fit
        max_chars = max_tokens * 4  # Rough estimation
        total_chars = 0
        included = []
        
        for msg in reversed(messages):
            msg_chars = len(msg["content"]) + 20  # +20 for role/formatting
            if total_chars + msg_chars < max_chars:
                included.insert(0, msg)
                total_chars += msg_chars
            else:
                break
        
        return included
    
    def get_context_summary(self):
        """Generate a summary of important context"""
        if not self.current_session:
            return ""
        
        summary_parts = []
        
        # Include important facts
        if self.current_session.get("important_facts"):
            summary_parts.append("[User Information]:")
            for key, value in self.current_session["important_facts"].items():
                readable_key = key.replace("_", " ").title()
                summary_parts.append(f"- {readable_key}: {value}")
        
        # Include recent memory items
        if self.current_session.get("memory_items"):
            recent_memories = self.current_session["memory_items"][-5:]  # Last 5
            if recent_memories:
                summary_parts.append("\n[Important Notes]:")
                for item in recent_memories:
                    summary_parts.append(f"- {item['content'][:100]}...")
        
        return "\n".join(summary_parts) if summary_parts else "No memory items yet."
    
    def save_session(self):
        """Save current session to disk"""
        if not self.current_session:
            return False
        
        try:
            filepath = config.CHAT_HISTORY_DIR / f"{self.current_session['id']}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"⚠ Error saving session: {e}")
            return False
    
    def load_session(self, session_id):
        """Load a session from disk"""
        try:
            filepath = config.CHAT_HISTORY_DIR / f"{session_id}.json"
            
            if not filepath.exists():
                print(f"⚠ Session file not found: {session_id}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                self.current_session = json.load(f)
            
            self.message_count = self.current_session.get("message_count", len(self.current_session["messages"]))
            print(f"✓ Loaded session: {session_id} ({self.message_count} messages)")
            
            return self.current_session
        except Exception as e:
            print(f"⚠ Error loading session: {e}")
            return None
    
    def list_sessions(self):
        """List all available sessions"""
        try:
            sessions = []
            for filepath in config.CHAT_HISTORY_DIR.glob("*.json"):
                session_id = filepath.stem
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append({
                            "id": session_id,
                            "created": data.get("created_at", "Unknown"),
                            "messages": data.get("message_count", len(data.get("messages", []))),
                            "last_updated": data.get("last_updated", "Unknown")
                        })
                except:
                    sessions.append({
                        "id": session_id,
                        "created": "Unknown",
                        "messages": 0,
                        "last_updated": "Unknown"
                    })
            
            # Sort by last updated, most recent first
            sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
            return sessions
        except Exception as e:
            print(f"⚠ Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id):
        """Delete a session"""
        try:
            filepath = config.CHAT_HISTORY_DIR / f"{session_id}.json"
            
            if filepath.exists():
                filepath.unlink()
                print(f"✓ Deleted session: {session_id}")
                return True
            else:
                print(f"⚠ Session not found: {session_id}")
                return False
        except Exception as e:
            print(f"⚠ Error deleting session: {e}")
            return False
    
    def export_session(self, session_id=None, format="txt"):
        """Export session to readable format"""
        if session_id:
            session_data = self.load_session(session_id)
        else:
            session_data = self.current_session
        
        if not session_data:
            return None
        
        if format == "txt":
            return self._export_as_text(session_data)
        elif format == "md":
            return self._export_as_markdown(session_data)
        else:
            return json.dumps(session_data, indent=2)
    
    def _export_as_text(self, session_data):
        """Export session as plain text"""
        lines = []
        lines.append(f"Chat Session: {session_data['id']}")
        lines.append(f"Created: {session_data.get('created_at', 'Unknown')}")
        lines.append(f"Messages: {len(session_data.get('messages', []))}")
        lines.append("=" * 60)
        lines.append("")
        
        for msg in session_data.get("messages", []):
            role = msg["role"].upper()
            timestamp = msg.get("timestamp", "")
            content = msg["content"]
            
            lines.append(f"[{timestamp}] {role}:")
            lines.append(content)
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_as_markdown(self, session_data):
        """Export session as markdown"""
        lines = []
        lines.append(f"# Chat Session: {session_data['id']}\n")
        lines.append(f"**Created:** {session_data.get('created_at', 'Unknown')}\n")
        lines.append(f"**Messages:** {len(session_data.get('messages', []))}\n")
        lines.append("---\n")
        
        for msg in session_data.get("messages", []):
            role = msg["role"].capitalize()
            content = msg["content"]
            
            if role == "User":
                lines.append(f"**👤 User:**\n{content}\n")
            else:
                lines.append(f"**🤖 Assistant:**\n{content}\n")
        
        return "\n".join(lines)
    
    def get_session_stats(self):
        """Get statistics about current session"""
        if not self.current_session:
            return None
        
        messages = self.current_session.get("messages", [])
        
        return {
            "total_messages": len(messages),
            "user_messages": sum(1 for m in messages if m["role"] == "user"),
            "assistant_messages": sum(1 for m in messages if m["role"] == "assistant"),
            "memory_items": len(self.current_session.get("memory_items", [])),
            "session_duration": self._calculate_duration(),
            "context_files": len(self.current_session.get("context_files", []))
        }
    
    def _calculate_duration(self):
        """Calculate session duration"""
        if not self.current_session or not self.current_session.get("created_at"):
            return "Unknown"
        
        try:
            created = datetime.fromisoformat(self.current_session["created_at"])
            now = datetime.now()
            duration = now - created
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"

# Global chat manager instance
chat_manager = ChatHistoryManager()
