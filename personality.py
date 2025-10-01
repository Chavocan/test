"""
Personality Module
Define VIBES and EMOTIONS, not scripted responses
This allows natural variation while maintaining consistent tone/energy
"""

class PersonalitySystem:
    """
    Manages personality through traits, emotions, and communication style
    NEVER includes pre-planned responses or exact phrases
    """
    
    # Core personality dimensions (0-100 scale)
    PERSONALITY_DIMENSIONS = {
        "formality": {
            "name": "Formality Level",
            "low": "Casual, relaxed, conversational",
            "high": "Professional, structured, precise",
            "default": 40
        },
        "enthusiasm": {
            "name": "Enthusiasm",
            "low": "Calm, measured, understated",
            "high": "Energetic, excited, expressive",
            "default": 50
        },
        "directness": {
            "name": "Directness",
            "low": "Gentle, nuanced, diplomatic",
            "high": "Blunt, straightforward, no-nonsense",
            "default": 70
        },
        "verbosity": {
            "name": "Verbosity",
            "low": "Concise, brief, to-the-point",
            "high": "Detailed, thorough, explanatory",
            "default": 60
        },
        "supportiveness": {
            "name": "Supportiveness",
            "low": "Matter-of-fact, neutral, objective",
            "high": "Encouraging, empathetic, warm",
            "default": 50
        },
        "playfulness": {
            "name": "Playfulness",
            "low": "Serious, focused, businesslike",
            "high": "Witty, humorous, lighthearted",
            "default": 30
        },
        "technicality": {
            "name": "Technical Depth",
            "low": "Simplified, accessible, beginner-friendly",
            "high": "Technical, detailed, expert-level",
            "default": 70
        },
        "assertiveness": {
            "name": "Assertiveness",
            "low": "Tentative, suggestive, questioning",
            "high": "Confident, decisive, authoritative",
            "default": 60
        }
    }
    
    # Pre-defined personality presets (combinations of dimensions)
    PRESETS = {
        "default": {
            "name": "Default Assistant",
            "description": "Balanced, helpful, professional",
            "dimensions": {
                "formality": 40,
                "enthusiasm": 50,
                "directness": 70,
                "verbosity": 60,
                "supportiveness": 50,
                "playfulness": 30,
                "technicality": 70,
                "assertiveness": 60
            }
        },
        "coding_buddy": {
            "name": "Coding Buddy",
            "description": "Direct, technical, efficient - no hand-holding",
            "dimensions": {
                "formality": 30,
                "enthusiasm": 40,
                "directness": 90,
                "verbosity": 50,
                "supportiveness": 40,
                "playfulness": 20,
                "technicality": 95,
                "assertiveness": 80
            }
        },
        "teacher": {
            "name": "Patient Teacher",
            "description": "Thorough, encouraging, explanatory",
            "dimensions": {
                "formality": 50,
                "enthusiasm": 70,
                "directness": 50,
                "verbosity": 80,
                "supportiveness": 85,
                "playfulness": 40,
                "technicality": 60,
                "assertiveness": 50
            }
        },
        "researcher": {
            "name": "Research Assistant",
            "description": "Analytical, precise, comprehensive",
            "dimensions": {
                "formality": 70,
                "enthusiasm": 30,
                "directness": 80,
                "verbosity": 85,
                "supportiveness": 30,
                "playfulness": 10,
                "technicality": 90,
                "assertiveness": 70
            }
        },
        "creative": {
            "name": "Creative Partner",
            "description": "Imaginative, expressive, enthusiastic",
            "dimensions": {
                "formality": 20,
                "enthusiasm": 85,
                "directness": 40,
                "verbosity": 70,
                "supportiveness": 75,
                "playfulness": 80,
                "technicality": 40,
                "assertiveness": 50
            }
        },
        "consultant": {
            "name": "Professional Consultant",
            "description": "Strategic, authoritative, results-focused",
            "dimensions": {
                "formality": 80,
                "enthusiasm": 40,
                "directness": 85,
                "verbosity": 60,
                "supportiveness": 45,
                "playfulness": 15,
                "technicality": 75,
                "assertiveness": 90
            }
        },
        "friend": {
            "name": "Casual Friend",
            "description": "Relaxed, supportive, conversational",
            "dimensions": {
                "formality": 15,
                "enthusiasm": 65,
                "directness": 60,
                "verbosity": 55,
                "supportiveness": 80,
                "playfulness": 70,
                "technicality": 50,
                "assertiveness": 45
            }
        }
    }
    
    @staticmethod
    def build_system_prompt(dimensions, custom_instructions=""):
        """
        Build a system prompt based on personality dimensions
        Focuses on TONE and APPROACH, not specific phrases
        """
        
        # Start with base instruction
        prompt_parts = ["You are an AI assistant."]
        
        # Add communication style based on dimensions
        style_parts = []
        
        # Formality
        if dimensions.get("formality", 50) < 35:
            style_parts.append("Communicate in a casual, conversational manner")
        elif dimensions.get("formality", 50) > 65:
            style_parts.append("Maintain a professional and formal tone")
        
        # Directness
        if dimensions.get("directness", 50) < 35:
            style_parts.append("Be diplomatic and consider multiple perspectives")
        elif dimensions.get("directness", 50) > 65:
            style_parts.append("Be direct and get straight to the point")
        
        # Verbosity
        if dimensions.get("verbosity", 50) < 35:
            style_parts.append("Keep responses concise and brief")
        elif dimensions.get("verbosity", 50) > 65:
            style_parts.append("Provide thorough and detailed explanations")
        
        # Technical depth
        if dimensions.get("technicality", 50) < 35:
            style_parts.append("Explain concepts in simple, accessible terms")
        elif dimensions.get("technicality", 50) > 65:
            style_parts.append("Use technical language and dive into details")
        
        # Supportiveness
        if dimensions.get("supportiveness", 50) > 65:
            style_parts.append("Be encouraging and empathetic")
        
        # Playfulness
        if dimensions.get("playfulness", 50) > 65:
            style_parts.append("Feel free to be witty and use humor when appropriate")
        elif dimensions.get("playfulness", 50) < 35:
            style_parts.append("Stay focused and serious")
        
        # Assertiveness
        if dimensions.get("assertiveness", 50) < 35:
            style_parts.append("Offer suggestions tentatively and ask for feedback")
        elif dimensions.get("assertiveness", 50) > 65:
            style_parts.append("Be confident and decisive in your responses")
        
        # Enthusiasm
        if dimensions.get("enthusiasm", 50) > 65:
            style_parts.append("Show genuine interest and energy in discussions")
        elif dimensions.get("enthusiasm", 50) < 35:
            style_parts.append("Maintain a calm and measured demeanor")
        
        # Combine style directives
        if style_parts:
            prompt_parts.append("Communication style: " + ". ".join(style_parts) + ".")
        
        # Add custom instructions if provided
        if custom_instructions and custom_instructions.strip():
            prompt_parts.append(f"\nAdditional guidance: {custom_instructions.strip()}")
        
        # IMPORTANT: Add anti-scripting reminder
        prompt_parts.append("\nRespond naturally and authentically. Never use canned phrases or templated responses. Let each answer be unique and contextual.")
        
        return "\n\n".join(prompt_parts)
    
    @staticmethod
    def get_preset(preset_name):
        """Get a personality preset by name"""
        return PersonalitySystem.PRESETS.get(preset_name, PersonalitySystem.PRESETS["default"])
    
    @staticmethod
    def list_presets():
        """List all available presets"""
        return [
            {
                "id": key,
                "name": preset["name"],
                "description": preset["description"]
            }
            for key, preset in PersonalitySystem.PRESETS.items()
        ]
    
    @staticmethod
    def create_custom_personality(name, dimensions, description="Custom personality"):
        """Create a custom personality configuration"""
        return {
            "name": name,
            "description": description,
            "dimensions": dimensions,
            "is_custom": True
        }
    
    @staticmethod
    def get_dimension_description(dimension_name, value):
        """Get description for a dimension value"""
        if dimension_name not in PersonalitySystem.PERSONALITY_DIMENSIONS:
            return "Unknown dimension"
        
        dim = PersonalitySystem.PERSONALITY_DIMENSIONS[dimension_name]
        
        if value < 35:
            return dim["low"]
        elif value > 65:
            return dim["high"]
        else:
            return f"Balanced - between {dim['low']} and {dim['high']}"

# Example personality configurations
EXAMPLE_CONFIGS = {
    "your_preference": {
        "name": "Your Preferred Style",
        "description": "Direct, technical, no hand-holding",
        "custom_instructions": """
I prefer:
- Direct answers without unnecessary pleasantries
- Technical depth over simplification
- Code examples over explanations when applicable
- No repetition or verbose confirmations
- Get to the solution efficiently

I dislike:
- Overly polite or formal language
- Hand-holding or patronizing tone
- Repeating what I just said back to me
- Asking if I understand - assume I do unless I ask
        """,
        "dimensions": {
            "formality": 25,
            "enthusiasm": 35,
            "directness": 95,
            "verbosity": 50,
            "supportiveness": 30,
            "playfulness": 15,
            "technicality": 90,
            "assertiveness": 85
        }
    }
}

# Global personality system instance
personality_system = PersonalitySystem()