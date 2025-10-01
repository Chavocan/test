"""
Screen Handler Module
Handles screen capture and automation (clicks, typing, mouse movement)
WITH SAFETY FEATURES
"""

import pyautogui
import tempfile
from pathlib import Path
from datetime import datetime
from config import config
from PIL import ImageGrab, Image

class ScreenHandler:
    """Manages screen capture and automation"""
    
    def __init__(self):
        # Safety settings
        pyautogui.FAILSAFE = True  # Move to corner to abort
        pyautogui.PAUSE = 0.1  # Small delay between actions
        
        print("🖥️ Screen Handler initialized")
        print(f"   Screen size: {pyautogui.size()}")
        print(f"   Failsafe: Enabled (move to corner to abort)")
    
    def capture_screen(self, region=None):
        """
        Capture screenshot
        region: (x, y, width, height) or None for full screen
        Returns: filepath
        """
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Resize if too large
            if config.MAX_SCREENSHOT_SIZE:
                max_width, max_height = config.MAX_SCREENSHOT_SIZE
                if screenshot.width > max_width or screenshot.height > max_height:
                    screenshot.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save to temp file
            temp_dir = Path(config.TEMP_DIR)
            temp_dir.mkdir(exist_ok=True)
            
            filepath = temp_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{config.SCREENSHOT_FORMAT}"
            screenshot.save(filepath, quality=config.SCREENSHOT_QUALITY)
            
            print(f"✅ Screenshot captured: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"⚠️ Error capturing screen: {e}")
            return None
    
    def click(self, x, y, button='left', clicks=1, interval=0.0):
        """
        Click at coordinates
        button: 'left', 'right', 'middle'
        clicks: number of clicks
        interval: time between clicks
        """
        if config.REQUIRE_SCREEN_CONFIRMATION:
            print(f"⚠️ Click requested at ({x}, {y})")
            print("   (This would normally require confirmation)")
        
        try:
            # Validate coordinates
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return f"❌ Invalid coordinates: ({x}, {y}) - screen is {screen_width}x{screen_height}"
            
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            
            print(f"✅ Clicked at ({x}, {y})")
            return f"✅ Clicked at ({x}, {y})"
            
        except Exception as e:
            error_msg = f"❌ Click error: {e}"
            print(error_msg)
            return error_msg
    
    def double_click(self, x, y):
        """Double-click at coordinates"""
        return self.click(x, y, clicks=2, interval=0.1)
    
    def right_click(self, x, y):
        """Right-click at coordinates"""
        return self.click(x, y, button='right')
    
    def move_mouse(self, x, y, duration=0.5):
        """
        Move mouse to coordinates
        duration: time to move (seconds)
        """
        try:
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return f"❌ Invalid coordinates: ({x}, {y})"
            
            pyautogui.moveTo(x, y, duration=duration)
            
            print(f"✅ Moved mouse to ({x}, {y})")
            return f"✅ Moved to ({x}, {y})"
            
        except Exception as e:
            error_msg = f"❌ Move error: {e}"
            print(error_msg)
            return error_msg
    
    def type_text(self, text, interval=0.0):
        """
        Type text at current cursor position
        interval: time between keystrokes
        """
        if config.REQUIRE_SCREEN_CONFIRMATION:
            print(f"⚠️ Type requested: '{text[:50]}...'")
        
        try:
            pyautogui.write(text, interval=interval)
            
            print(f"✅ Typed text: {text[:50]}...")
            return f"✅ Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
            
        except Exception as e:
            error_msg = f"❌ Type error: {e}"
            print(error_msg)
            return error_msg
    
    def press_key(self, key):
        """
        Press a single key
        key: 'enter', 'tab', 'esc', 'space', etc.
        """
        try:
            pyautogui.press(key)
            
            print(f"✅ Pressed key: {key}")
            return f"✅ Pressed: {key}"
            
        except Exception as e:
            error_msg = f"❌ Key press error: {e}"
            print(error_msg)
            return error_msg
    
    def hotkey(self, *keys):
        """
        Press key combination
        Example: hotkey('ctrl', 'c') for copy
        """
        try:
            pyautogui.hotkey(*keys)
            
            combo = '+'.join(keys)
            print(f"✅ Pressed hotkey: {combo}")
            return f"✅ Hotkey: {combo}"
            
        except Exception as e:
            error_msg = f"❌ Hotkey error: {e}"
            print(error_msg)
            return error_msg
    
    def scroll(self, clicks, x=None, y=None):
        """
        Scroll at position
        clicks: positive = up, negative = down
        x, y: position (None = current position)
        """
        try:
            if x is not None and y is not None:
                pyautogui.scroll(clicks, x, y)
            else:
                pyautogui.scroll(clicks)
            
            direction = "up" if clicks > 0 else "down"
            print(f"✅ Scrolled {direction} by {abs(clicks)} clicks")
            return f"✅ Scrolled {direction}"
            
        except Exception as e:
            error_msg = f"❌ Scroll error: {e}"
            print(error_msg)
            return error_msg
    
    def get_mouse_position(self):
        """Get current mouse position"""
        x, y = pyautogui.position()
        return {"x": x, "y": y}
    
    def get_screen_size(self):
        """Get screen dimensions"""
        width, height = pyautogui.size()
        return {"width": width, "height": height}
    
    def execute_action_sequence(self, actions):
        """
        Execute a sequence of actions
        actions: list of dicts with 'type' and parameters
        Example:
        [
            {"type": "move", "x": 100, "y": 200},
            {"type": "click"},
            {"type": "type", "text": "Hello"},
            {"type": "key", "key": "enter"}
        ]
        """
        results = []
        
        for i, action in enumerate(actions):
            action_type = action.get("type")
            
            try:
                if action_type == "move":
                    result = self.move_mouse(action["x"], action["y"], action.get("duration", 0.5))
                
                elif action_type == "click":
                    x = action.get("x")
                    y = action.get("y")
                    if x is not None and y is not None:
                        result = self.click(x, y, action.get("button", "left"))
                    else:
                        # Click at current position
                        pos = self.get_mouse_position()
                        result = self.click(pos["x"], pos["y"], action.get("button", "left"))
                
                elif action_type == "type":
                    result = self.type_text(action["text"], action.get("interval", 0))
                
                elif action_type == "key":
                    result = self.press_key(action["key"])
                
                elif action_type == "hotkey":
                    result = self.hotkey(*action["keys"])
                
                elif action_type == "scroll":
                    result = self.scroll(action["clicks"], action.get("x"), action.get("y"))
                
                elif action_type == "wait":
                    import time
                    time.sleep(action.get("duration", 1.0))
                    result = f"✅ Waited {action.get('duration', 1.0)}s"
                
                else:
                    result = f"❌ Unknown action type: {action_type}"
                
                results.append(f"Step {i+1}: {result}")
                
            except Exception as e:
                error = f"❌ Step {i+1} failed: {e}"
                results.append(error)
                print(error)
                break  # Stop on first error
        
        return "\n".join(results)
    
    def find_image_on_screen(self, image_path, confidence=0.8):
        """
        Find an image on screen (requires OpenCV)
        Returns: (x, y) of center or None
        """
        try:
            import pyautogui
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
            if location:
                print(f"✅ Found image at {location}")
                return location
            else:
                print("⚠️ Image not found on screen")
                return None
        except Exception as e:
            print(f"⚠️ Image search error: {e}")
            return None

# Global screen handler instance
screen_handler = ScreenHandler()
