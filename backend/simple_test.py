#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("1. Starting test...")

try:
    print("2. Importing TextSummarizer...")
    from app.services.text_summarizer import TextSummarizer
    print("3. Import successful!")
    
    print("4. Creating instance...")
    summarizer = TextSummarizer()
    print("5. Instance created successfully!")
    
    print("6. Done!")
    
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Other Error: {e}")
    import traceback
    traceback.print_exc()
