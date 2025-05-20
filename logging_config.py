import os
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def configure_logging(app):
    """Configure logging for the application"""
    
    # Configure Sentry for error tracking
    if os.getenv('SENTRY_DSN'):
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            environment=os.getenv('FLASK_ENV', 'development')
        )
    
    # Set up file logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/xoxo.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    
    # Set the log format
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    
    # Set the log level
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Set the app logger level
    app.logger.setLevel(logging.INFO)
    app.logger.info('XOXO By SLOG startup')
    
    # Add console handler for development
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Debug mode enabled') 