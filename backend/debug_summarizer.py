#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing TextSummarizer model persistence...")

try:
    from app.services.text_summarizer import TextSummarizer
    print('✅ Import successful!')
    
    print("Creating TextSummarizer instance...")
    summarizer = TextSummarizer()
    print('✅ TextSummarizer initialized!')
    
    print(f'Model name: {getattr(summarizer, "model_name", "NOT SET")}')
    print(f'Model status loaded: {summarizer.model_status.loaded}')
    print(f'Model status name: {summarizer.model_status.model_name}')
    print(f'Summarizer model: {summarizer._summarizer is not None}')
    print(f'Summarizer tokenizer: {summarizer._summarizer_tokenizer is not None}')
    
    # Test summary generation
    if summarizer._summarizer is not None:
        print("\n🔬 Testing summary generation...")
        test_text = "El fútbol es un deporte muy popular en España. Los jugadores corren por el campo y tratan de meter goles. Es muy emocionante de ver."
        result = summarizer.generate_summary(test_text)
        print(f"Summary result: {result.get('summary', 'NO SUMMARY')[:100]}...")
    else:
        print("⚠️ No model loaded for testing")
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
