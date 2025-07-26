"""
WSGI Entry Point for Production Deployment
Optimized for Gunicorn, uWSGI, and cloud platforms
"""

import os
import logging
from app import ChatbotApp
from production_config import ProductionConfig

# Configure production logging
logging.basicConfig(
    level=getattr(logging, ProductionConfig.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Application factory for production deployment."""
    
    # Validate production environment
    required_vars, warnings = ProductionConfig.validate_production_env()
    
    if required_vars:
        logger.error(f"Missing required environment variables: {required_vars}")
        raise ValueError(f"Missing required environment variables: {required_vars}")
    
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    
    # Create application instance
    chatbot_app = ChatbotApp()
    
    # Apply production configuration
    chatbot_app.app.config.from_object(ProductionConfig)
    
    logger.info("CHAI Chatbot Interface started in production mode")
    logger.info(f"Configured for host: {ProductionConfig.HOST}:{ProductionConfig.PORT}")
    
    return chatbot_app.app

# Create the application instance
application = create_app()
app = application  # For compatibility with various WSGI servers

if __name__ == '__main__':
    # For direct execution (not recommended in production)
    app.run(
        host=ProductionConfig.HOST,
        port=ProductionConfig.PORT,
        debug=False
    )