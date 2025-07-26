"""
Configuration module for the CHAI Chatbot Interface.
Elegant, centralized configuration management.
"""

import os
from typing import Dict, Any


class Config:
    """Elegant configuration class with immutable settings."""
    
    # CHAI API Configuration
    CHAI_API_URL = "http://guanaco-submitter.guanaco-backend.k2.chaiverse.com/endpoints/onsite/chat"
    CHAI_API_TOKEN = "CR_14d43f2bf78b4b0590c2a8b87f354746"
    
    # Application Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Chat Configuration
    DEFAULT_BOT_NAME = "Assistant"
    DEFAULT_USER_NAME = "User"
    SAFETY_PROMPT = (
        "This conversation must be family friendly. Avoid using profanity, or being rude. "
        "Be courteous and use language which is appropriate for any audience. "
        "Avoid NSFW content. ###"
    )
    
    # Request Configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get API headers with proper authorization."""
        return {
            "Authorization": f"Bearer {cls.CHAI_API_TOKEN}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary for debugging."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }