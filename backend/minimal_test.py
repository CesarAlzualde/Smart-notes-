#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("1. Starting...")

try:
    print("2. Testing individual imports...")
    
    print("2a. Import nltk...")
    import nltk
    print("2b. Import torch...")
    import torch
    print("2c. Import transformers...")
    from transformers import AutoTokenizer
    print("2d. All core imports work!")
    
    print("3. Testing module import...")
    from app.services import text_summarizer
    print("4. Module imported!")
    
    print("5. Testing class access...")
    TextSummarizer = text_summarizer.TextSummarizer
    print("6. Class accessed!")
    
    print("✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
