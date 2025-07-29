#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing import only...")

try:
    from app.services.text_summarizer import TextSummarizer
    print("✅ Import successful!")
    print("✅ TextSummarizer class is available")
    
    # Test if the class exists and is callable
    print(f"TextSummarizer class: {TextSummarizer}")
    print(f"Is callable: {callable(TextSummarizer)}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
