import logging
import sys
import os
from logging.handlers import RotatingFileHandler

# Create log directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 1. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler (General Info)
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "app.log"), maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 3. Error File Handler
        error_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "error.log"), maxBytes=10*1024*1024, backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger

def setup_llm_logger(name: str = "llm"):
    """
    Specialized logger for LLM interactions (chains, full prompts, responses).
    Writes to app/log/llm.log
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s'
        )
        
        # LLM File Handler
        llm_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, "llm.log"), maxBytes=10*1024*1024, backupCount=5
        )
        llm_handler.setLevel(logging.INFO)
        llm_handler.setFormatter(formatter)
        logger.addHandler(llm_handler)
        
    return logger
    return logger
