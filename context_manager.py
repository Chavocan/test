"""
Context Manager Module
Handles persistent context files for cross-session knowledge
"""

import os
from pathlib import Path
from datetime import datetime
from config import config

class ContextFileManager:
    """Manages context files for persistent knowledge across sessions"""
    
    def __init__(self):
        self.loaded_files = {}  # Cache loaded files
    
    def create_context_file(self, content, name=None, category=None):
        """Create a new context file"""
        if not name:
            name = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Ensure .txt extension
        if not name.endswith('.txt'):
            name += '.txt'
        
        # Handle category subdirectories
        if category:
            category_dir = config.CONTEXT_FILES_DIR / category
            category_dir.mkdir(exist_ok=True)
            filepath = category_dir / name
        else:
            filepath = config.CONTEXT_FILES_DIR / name
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Created context file: {name}")
            return str(filepath)
        except Exception as e:
            print(f"⚠ Error creating context file: {e}")
            return None
    
    def load_context_file(self, name, use_cache=True):
        """Load a context file"""
        # Check cache first
        if use_cache and name in self.loaded_files:
            return self.loaded_files[name]
        
        # Try direct path
        filepath = config.CONTEXT_FILES_DIR / name
        
        # If not found, search in subdirectories
        if not filepath.exists():
            for subdir in config.CONTEXT_FILES_DIR.iterdir():
                if subdir.is_dir():
                    potential_path = subdir / name
                    if potential_path.exists():
                        filepath = potential_path
                        break
        
        if not filepath.exists():
            print(f"⚠ Context file not found: {name}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache the content
            if use_cache:
                self.loaded_files[name] = content
            
            return content
        except Exception as e:
            print(f"⚠ Error loading context file: {e}")
            return None
    
    def update_context_file(self, name, content, append=False):
        """Update an existing context file"""
        filepath = config.CONTEXT_FILES_DIR / name
        
        # Search in subdirectories if not found
        if not filepath.exists():
            for subdir in config.CONTEXT_FILES_DIR.iterdir():
                if subdir.is_dir():
                    potential_path = subdir / name
                    if potential_path.exists():
                        filepath = potential_path
                        break
        
        if not filepath.exists():
            print(f"⚠ Context file not found: {name}")
            return False
        
        try:
            mode = 'a' if append else 'w'
            with open(filepath, mode, encoding='utf-8') as f:
                if append:
                    f.write('\n' + content)
                else:
                    f.write(content)
            
            # Invalidate cache
            if name in self.loaded_files:
                del self.loaded_files[name]
            
            print(f"✓ Updated context file: {name}")
            return True
        except Exception as e:
            print(f"⚠ Error updating context file: {e}")
            return False
    
    def delete_context_file(self, name):
        """Delete a context file"""
        filepath = config.CONTEXT_FILES_DIR / name
        
        # Search in subdirectories
        if not filepath.exists():
            for subdir in config.CONTEXT_FILES_DIR.iterdir():
                if subdir.is_dir():
                    potential_path = subdir / name
                    if potential_path.exists():
                        filepath = potential_path
                        break
        
        if not filepath.exists():
            print(f"⚠ Context file not found: {name}")
            return False
        
        try:
            filepath.unlink()
            
            # Remove from cache
            if name in self.loaded_files:
                del self.loaded_files[name]
            
            print(f"✓ Deleted context file: {name}")
            return True
        except Exception as e:
            print(f"⚠ Error deleting context file: {e}")
            return False
    
    def list_context_files(self, category=None):
        """List all context files, optionally filtered by category"""
        files = []
        
        if category:
            search_dir = config.CONTEXT_FILES_DIR / category
            if not search_dir.exists():
                return []
        else:
            search_dir = config.CONTEXT_FILES_DIR
        
        try:
            # Get files in main directory
            for filepath in search_dir.glob('*.txt'):
                if filepath.is_file():
                    files.append({
                        "name": filepath.name,
                        "path": str(filepath.relative_to(config.CONTEXT_FILES_DIR)),
                        "size": filepath.stat().st_size,
                        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                        "category": filepath.parent.name if filepath.parent != config.CONTEXT_FILES_DIR else None
                    })
            
            # Also search subdirectories if no specific category
            if not category:
                for subdir in config.CONTEXT_FILES_DIR.iterdir():
                    if subdir.is_dir():
                        for filepath in subdir.glob('*.txt'):
                            if filepath.is_file():
                                files.append({
                                    "name": filepath.name,
                                    "path": str(filepath.relative_to(config.CONTEXT_FILES_DIR)),
                                    "size": filepath.stat().st_size,
                                    "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                                    "category": subdir.name
                                })
            
            # Sort by modified date, most recent first
            files.sort(key=lambda x: x["modified"], reverse=True)
            
            return files
        except Exception as e:
            print(f"⚠ Error listing context files: {e}")
            return []
    
    def get_context_files_content(self, file_names, max_tokens=None):
        """Load multiple context files and combine their content"""
        if not file_names:
            return ""
        
        if max_tokens is None:
            max_tokens = config.CONTEXT_TOKEN_BUDGET
        
        max_chars = max_tokens * 4  # Rough estimation
        
        contents = []
        total_chars = 0
        
        for name in file_names:
            if total_chars >= max_chars:
                print(f"⚠ Context token budget reached, skipping remaining files")
                break
            
            content = self.load_context_file(name)
            if content:
                # Truncate if needed
                available_chars = max_chars - total_chars
                if len(content) > available_chars:
                    content = content[:available_chars] + "\n[... truncated]"
                
                contents.append(f"[Context from {name}]:\n{content}\n")
                total_chars += len(content)
        
        return "\n".join(contents)
    
    def search_context_files(self, query):
        """Search for files containing a specific query"""
        results = []
        
        for file_info in self.list_context_files():
            content = self.load_context_file(file_info["name"])
            if content and query.lower() in content.lower():
                # Find context around the match
                query_pos = content.lower().find(query.lower())
                start = max(0, query_pos - 50)
                end = min(len(content), query_pos + len(query) + 50)
                snippet = content[start:end]
                
                results.append({
                    "file": file_info["name"],
                    "snippet": f"...{snippet}...",
                    "category": file_info.get("category")
                })
        
        return results
    
    def get_file_stats(self, name):
        """Get statistics about a context file"""
        content = self.load_context_file(name)
        if not content:
            return None
        
        return {
            "name": name,
            "characters": len(content),
            "words": len(content.split()),
            "lines": len(content.split('\n')),
            "estimated_tokens": len(content) // 4
        }
    
    def create_category(self, category_name):
        """Create a new category (subdirectory) for organizing files"""
        category_dir = config.CONTEXT_FILES_DIR / category_name
        
        try:
            category_dir.mkdir(exist_ok=True)
            print(f"✓ Created category: {category_name}")
            return True
        except Exception as e:
            print(f"⚠ Error creating category: {e}")
            return False
    
    def list_categories(self):
        """List all available categories"""
        categories = ["(root)"]  # Main directory
        
        try:
            for subdir in config.CONTEXT_FILES_DIR.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    categories.append(subdir.name)
            
            return sorted(categories)
        except Exception as e:
            print(f"⚠ Error listing categories: {e}")
            return []
    
    def move_file(self, name, new_category):
        """Move a file to a different category"""
        # Find current file
        current_path = config.CONTEXT_FILES_DIR / name
        
        if not current_path.exists():
            for subdir in config.CONTEXT_FILES_DIR.iterdir():
                if subdir.is_dir():
                    potential_path = subdir / name
                    if potential_path.exists():
                        current_path = potential_path
                        break
        
        if not current_path.exists():
            print(f"⚠ Context file not found: {name}")
            return False
        
        # Determine new path
        if new_category and new_category != "(root)":
            new_dir = config.CONTEXT_FILES_DIR / new_category
            new_dir.mkdir(exist_ok=True)
            new_path = new_dir / name
        else:
            new_path = config.CONTEXT_FILES_DIR / name
        
        try:
            current_path.rename(new_path)
            
            # Invalidate cache
            if name in self.loaded_files:
                del self.loaded_files[name]
            
            print(f"✓ Moved {name} to {new_category or 'root'}")
            return True
        except Exception as e:
            print(f"⚠ Error moving file: {e}")
            return False
    
    def clear_cache(self):
        """Clear the file content cache"""
        self.loaded_files.clear()
        print("✓ Context file cache cleared")

# Global context manager instance
context_manager = ContextFileManager()