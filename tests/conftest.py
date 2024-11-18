"""Pytest configuration file"""

import os
import sys
import pytest
import logging
from datetime import datetime

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup logging for pytest
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Configure logging for pytest session"""
    logs_dir = os.path.join(project_root, 'logs', 'tests')
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(logs_dir, f'pytest_log_{timestamp}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

@pytest.fixture(scope="session")
def chatbot():
    """Fixture to create a chatbot instance that can be reused across tests"""
    from src.main.simple_faq_chatbot import SimpleFAQChatbot
    return SimpleFAQChatbot('data/highrise_faq.json') 