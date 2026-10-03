"""
Test script for NLG integration
This script tests the NLG generator without requiring a running MongoDB server
"""

import os
import sys

# Set a test API key if not present (for testing only)
if not os.environ.get('GEMINI_API_KEY'):
    print("Warning: GEMINI_API_KEY not set. NLG will not work without a valid API key.")
    print("Please set GEMINI_API_KEY in your .env file or environment variables.")
    print("\nTo get a Gemini API key:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Add it to your .env file: GEMINI_API_KEY=your_key_here")
    sys.exit(1)

from ml.nlg_generator import get_nlg_generator

def test_nlg_generator():
    """Test the NLG generator with sample data"""
    print("Testing NLG Generator...")
    print("=" * 50)
    
    # Get the NLG generator
    nlg = get_nlg_generator()
    
    # Check if available
    if not nlg.is_available():
        print("❌ NLG Generator is not available (API key missing or invalid)")
        return False
    
    print("✅ NLG Generator initialized successfully")
    
    # Test with sample data
    test_question = "What are the library timings?"
    test_context = {
        'library': {
            'timings': '8 AM - 10 PM',
            'max_books': '5',
            'fine_per_day': '5'
        }
    }
    test_history = [
        {'question': 'Where is the library located?', 'answer': 'The library is in the main building.'}
    ]
    
    print(f"\nTest Question: {test_question}")
    print(f"Context: {test_context}")
    print(f"Conversation History: {len(test_history)} previous exchanges")
    
    try:
        response = nlg.generate_response(
            question=test_question,
            context=test_context,
            conversation_history=test_history
        )
        
        if response:
            print(f"\n✅ NLG Response Generated:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            return True
        else:
            print("❌ NLG returned None (generation failed)")
            return False
            
    except Exception as e:
        print(f"❌ Error during NLG generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_mechanism():
    """Test that the system can fall back to FAQ when NLG fails"""
    print("\n\nTesting Fallback Mechanism...")
    print("=" * 50)
    
    # Test with invalid API key scenario
    original_key = os.environ.get('GEMINI_API_KEY')
    os.environ['GEMINI_API_KEY'] = 'invalid_key'
    
    # Force reload
    from ml import nlg_generator
    nlg_generator.nlg_generator = None
    
    nlg = get_nlg_generator()
    
    if not nlg.is_available():
        print("✅ Fallback mechanism working: NLG unavailable when API key is invalid")
    else:
        print("❌ Fallback mechanism issue: NLG available with invalid key")
    
    # Restore original key
    if original_key:
        os.environ['GEMINI_API_KEY'] = original_key
    else:
        os.environ.pop('GEMINI_API_KEY', None)
    
    # Force reload again
    nlg_generator.nlg_generator = None
    
    return True

if __name__ == '__main__':
    print("NLG Integration Test Suite")
    print("=" * 50)
    
    # Test NLG generator
    nlg_works = test_nlg_generator()
    
    # Test fallback
    fallback_works = test_fallback_mechanism()
    
    print("\n\n" + "=" * 50)
    print("Test Results:")
    print(f"NLG Generation: {'✅ PASS' if nlg_works else '❌ FAIL'}")
    print(f"Fallback Mechanism: {'✅ PASS' if fallback_works else '❌ FAIL'}")
    print("=" * 50)
    
    if nlg_works and fallback_works:
        print("\n🎉 All tests passed! NLG integration is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)
