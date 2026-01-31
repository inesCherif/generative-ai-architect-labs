"""
Configuration Module for RAG Pipeline

This module handles:
- Loading environment variables (API keys)
- Setting up model configurations
- Managing file paths

Think of this as the "settings panel" for your RAG system.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for RAG pipeline
    
    This centralizes all settings so they're easy to change in one place.
    """
    
    # === API Keys ===
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # === File Paths ===
    # Get the project root directory
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # === Model Settings ===
    # Embedding model - converts text to vectors
    # We use a local model (no API needed!) that's fast and free
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # LLM Settings
    LLM_MODEL = "gpt-3.5-turbo"  # Fast and cost-effective
    LLM_TEMPERATURE = 0.7  # 0 = deterministic, 1 = creative
    LLM_MAX_TOKENS = 500  # Maximum length of response
    
    # === RAG Settings ===
    # How many documents to retrieve for each query
    TOP_K_RESULTS = 3
    
    # Chunk size: how to split large documents
    CHUNK_SIZE = 500  # characters per chunk
    CHUNK_OVERLAP = 50  # overlap between chunks (prevents cutting sentences)
    
    # === Vector Database Settings ===
    VECTOR_DB_PATH = BASE_DIR / "vector_db"
    
    @classmethod
    def validate(cls):
        """
        Check if all required settings are present
        
        This is like a "pre-flight check" before takeoff!
        """
        if not cls.OPENAI_API_KEY:
            print("⚠️  WARNING: OPENAI_API_KEY not found in .env file")
            print("    You'll need this to use the LLM for generation.")
            print("    Get your key from: https://platform.openai.com/api-keys")
            return False
        
        if not cls.DATA_DIR.exists():
            print(f"⚠️  WARNING: Data directory not found: {cls.DATA_DIR}")
            return False
            
        print("✅ Configuration validated successfully!")
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without revealing API keys!)"""
        print("\n" + "="*50)
        print("🔧 RAG PIPELINE CONFIGURATION")
        print("="*50)
        print(f"📁 Data Directory: {cls.DATA_DIR}")
        print(f"📊 Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"🤖 LLM Model: {cls.LLM_MODEL}")
        print(f"🔍 Top-K Results: {cls.TOP_K_RESULTS}")
        print(f"📄 Chunk Size: {cls.CHUNK_SIZE} characters")
        print(f"🔑 OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Missing'}")
        print("="*50 + "\n")


if __name__ == "__main__":
    # Test the configuration
    Config.print_config()
    Config.validate()