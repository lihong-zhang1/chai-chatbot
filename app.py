"""
CHAI Chatbot Web Interface - Flask Backend
Elegant, minimalist web server with robust error handling.
"""

from flask import Flask, render_template, request, jsonify, session
from typing import Dict, List, Any
import uuid
import logging
from datetime import datetime

from config import Config
from chai_client import chai_client, ChatMessage
from security_middleware import SecurityMiddleware, rate_limit


# Configure elegant logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatbotApp:
    """Elegant Flask application wrapper with session management."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = Config.SECRET_KEY
        
        # Initialize security middleware
        self.security = SecurityMiddleware(self.app)
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Configure application routes with elegant handlers."""
        
        @self.app.route('/')
        def index():
            """Serve the main chat interface."""
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
                session['chat_history'] = []
                logger.info(f"New session created: {session['session_id']}")
            
            return render_template('index.html')
        
        @self.app.route('/api/chat', methods=['POST'])
        @rate_limit(limit=5, window=60)  # 5 requests per minute for chat
        def chat():
            """Handle chat API requests with elegant error handling."""
            try:
                data = request.get_json()
                
                if not data or 'message' not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing message in request'
                    }), 400
                
                user_message = data['message'].strip()
                if not user_message:
                    return jsonify({
                        'success': False,
                        'error': 'Empty message not allowed'
                    }), 400
                
                # Get session data
                session_id = session.get('session_id', str(uuid.uuid4()))
                chat_history = session.get('chat_history', [])
                
                # Extract optional parameters
                bot_name = data.get('bot_name', Config.DEFAULT_BOT_NAME)
                user_name = data.get('user_name', Config.DEFAULT_USER_NAME)
                custom_prompt = data.get('custom_prompt')
                
                logger.info(f"Processing chat request for session: {session_id}")
                
                # Create and send request to CHAI API
                chat_request = chai_client.create_chat_request(
                    user_message=user_message,
                    chat_history=chat_history,
                    bot_name=bot_name,
                    user_name=user_name,
                    custom_prompt=custom_prompt
                )
                
                success, response, error = chai_client.send_message(chat_request)
                
                if success:
                    # Update session history
                    chat_history.append({
                        'sender': user_name,
                        'message': user_message,
                        'timestamp': datetime.now().isoformat()
                    })
                    chat_history.append({
                        'sender': bot_name,
                        'message': response,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    session['chat_history'] = chat_history
                    
                    return jsonify({
                        'success': True,
                        'response': response,
                        'bot_name': bot_name,
                        'user_name': user_name
                    })
                else:
                    logger.error(f"CHAI API error for session {session_id}: {error}")
                    return jsonify({
                        'success': False,
                        'error': f'Chat service error: {error}'
                    }), 500
                    
            except Exception as e:
                logger.error(f"Unexpected error in chat endpoint: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Internal server error'
                }), 500
        
        @self.app.route('/api/history')
        def get_history():
            """Get chat history for current session."""
            try:
                history = session.get('chat_history', [])
                return jsonify({
                    'success': True,
                    'history': history,
                    'session_id': session.get('session_id')
                })
            except Exception as e:
                logger.error(f"Error retrieving history: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to retrieve chat history'
                }), 500
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_history():
            """Clear chat history for current session."""
            try:
                session['chat_history'] = []
                logger.info(f"History cleared for session: {session.get('session_id')}")
                return jsonify({
                    'success': True,
                    'message': 'Chat history cleared'
                })
            except Exception as e:
                logger.error(f"Error clearing history: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to clear chat history'
                }), 500
        
        @self.app.route('/api/config')
        def get_config():
            """Get public configuration for frontend."""
            return jsonify({
                'bot_name': Config.DEFAULT_BOT_NAME,
                'user_name': Config.DEFAULT_USER_NAME,
                'safety_prompt': Config.SAFETY_PROMPT
            })
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Elegant 404 handler."""
            return jsonify({
                'success': False,
                'error': 'Endpoint not found'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Elegant 500 handler."""
            logger.error(f"Internal server error: {str(error)}")
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the application with elegant configuration."""
        host = host or Config.HOST
        port = port or Config.PORT
        debug = debug if debug is not None else Config.DEBUG
        
        logger.info(f"Starting CHAI Chatbot Interface on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        self.app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )


def main():
    """Application entry point."""
    chatbot_app = ChatbotApp()
    chatbot_app.run()


if __name__ == '__main__':
    main()