"""
CHAI API Client - Elegant interface to CHAI's model API.
Implements robust communication with graceful error handling.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config


# Configure logging with elegant formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Immutable chat message representation."""
    sender: str
    message: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API consumption."""
        return asdict(self)


@dataclass 
class ChatRequest:
    """Structured chat request with validation."""
    prompt: str
    bot_name: str
    user_name: str
    chat_history: List[ChatMessage]
    memory: str = ""
    
    def to_payload(self) -> Dict:
        """Convert to API payload format."""
        return {
            "memory": self.memory,
            "prompt": self.prompt,
            "bot_name": self.bot_name,
            "user_name": self.user_name,
            "chat_history": [msg.to_dict() for msg in self.chat_history]
        }


class ChaiAPIClient:
    """
    Elegant CHAI API client with robust error handling and retry logic.
    Implements the circuit breaker pattern for resilience.
    """
    
    def __init__(self):
        self.session = self._create_session()
        self.config = Config()
        
    def _create_session(self) -> requests.Session:
        """Create a robust HTTP session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def send_message(self, request: ChatRequest) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send message to CHAI API with elegant error handling.
        
        Returns:
            Tuple[success: bool, response: Optional[str], error: Optional[str]]
        """
        try:
            payload = request.to_payload()
            logger.info(f"Sending request to CHAI API for bot: {request.bot_name}")
            
            response = self.session.post(
                Config.CHAI_API_URL,
                headers=Config.get_headers(),
                json=payload,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    response_text = response_data.get("model_output", "No response")
                    logger.info("Successfully received response from CHAI API")
                    return True, response_text, None
                except json.JSONDecodeError:
                    # Fallback to raw text if JSON parsing fails
                    response_text = response.text.strip()
                    logger.info("Successfully received response from CHAI API (raw text)")
                    return True, response_text, None
            else:
                error_msg = f"API returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Request timed out"
            logger.error(error_msg)
            return False, None, error_msg
            
        except requests.exceptions.ConnectionError:
            error_msg = "Failed to connect to CHAI API"
            logger.error(error_msg)
            return False, None, error_msg
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def create_chat_request(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]] = None,
        bot_name: str = None,
        user_name: str = None,
        custom_prompt: str = None
    ) -> ChatRequest:
        """
        Factory method to create a properly formatted chat request.
        """
        bot_name = bot_name or Config.DEFAULT_BOT_NAME
        user_name = user_name or Config.DEFAULT_USER_NAME
        prompt = custom_prompt or Config.SAFETY_PROMPT
        
        # Convert history to ChatMessage objects
        history = []
        if chat_history:
            history = [
                ChatMessage(sender=msg["sender"], message=msg["message"])
                for msg in chat_history
            ]
        
        # Add current user message
        history.append(ChatMessage(sender=user_name, message=user_message))
        
        return ChatRequest(
            prompt=prompt,
            bot_name=bot_name,
            user_name=user_name,
            chat_history=history
        )


# Singleton instance for elegant usage
chai_client = ChaiAPIClient()