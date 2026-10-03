"""
Test script for semantic matching improvements
Tests different wordings of the same question to ensure they retrieve the same intent
"""

import sys
import os

# Ensure we can import from the ml module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.semantic_matcher import get_semantic_matcher, build_semantic_embeddings_if_needed
from ml.predict import predict_intent

def test_semantic_library_questions():
    """Test semantically similar questions about library timings"""
    print("=" * 70)
    print("Testing Semantic Matching: Library Timings")
    print("=" * 70)
    
    # Build semantic embeddings if needed
    semantic_matcher = build_semantic_embeddings_if_needed()
    
    if not semantic_matcher.is_available():
        print("X Semantic matcher not available")
        return False
    
    # Test questions with the same meaning but different wordings
    test_questions = [
        "What are the timings of the library?",
        "At which time does the library open?",
        "When is the library open?",
        "Library hours",
        "What time does library close?",
        "What are library opening hours?",
        "When does the library open and close?",
        "Library schedule",
        "Is the library open now?",
        "What time is the library open until?"
    ]
    
    results = []
    for question in test_questions:
        # Test with semantic matcher
        intent, confidence, pattern, matches = semantic_matcher.find_best_match(question, threshold=0.4)
        
        # Test with full predict function
        pred_intent, pred_confidence, pred_response, pred_context = predict_intent(question, return_context=True)
        
        results.append({
            'question': question,
            'semantic_intent': intent,
            'semantic_confidence': confidence,
            'predict_intent': pred_intent,
            'predict_confidence': pred_confidence,
            'predict_source': pred_context.get('confidence_source', 'unknown'),
            'matched_pattern': pattern
        })
        
        print(f"\nQuestion: {question}")
        print(f"  Semantic: {intent} ({confidence:.3f})")
        print(f"  Predict:  {pred_intent} ({pred_confidence:.3f}) [{pred_context.get('confidence_source', 'unknown')}]")
        if pattern:
            print(f"  Pattern:  {pattern}")
    
    # Analyze consistency
    print("\n" + "=" * 70)
    print("Consistency Analysis")
    print("=" * 70)
    
    intents = [r['predict_intent'] for r in results]
    unique_intents = set(intents)
    
    print(f"Total questions tested: {len(test_questions)}")
    print(f"Unique intents found: {len(unique_intents)}")
    print(f"Intents: {unique_intents}")
    
    if len(unique_intents) == 1:
        print("OK All questions mapped to the same intent - GOOD!")
        return True
    else:
        print("WARN Questions mapped to different intents - needs improvement")
        
        # Show distribution
        from collections import Counter
        intent_counts = Counter(intents)
        print("\nIntent distribution:")
        for intent, count in intent_counts.items():
            print(f"  {intent}: {count} questions")
        
        return False

def test_semantic_fee_questions():
    """Test semantically similar questions about fees"""
    print("\n" + "=" * 70)
    print("Testing Semantic Matching: Fee Structure")
    print("=" * 70)
    
    test_questions = [
        "What is the fee structure?",
        "How much are the fees?",
        "Tell me about the fees",
        "Fee details",
        "What are the charges?",
        "How much does it cost?",
        "What is the total fee?",
        "Fee information",
        "Cost of study",
        "What are the tuition fees?"
    ]
    
    results = []
    for question in test_questions:
        pred_intent, pred_confidence, pred_response, pred_context = predict_intent(question, return_context=True)
        
        results.append({
            'question': question,
            'intent': pred_intent,
            'confidence': pred_confidence,
            'source': pred_context.get('confidence_source', 'unknown')
        })
        
        print(f"\nQuestion: {question}")
        print(f"  Intent: {pred_intent} ({pred_confidence:.3f}) [{pred_context.get('confidence_source', 'unknown')}]")
    
    # Analyze consistency
    intents = [r['intent'] for r in results]
    unique_intents = set(intents)
    
    print(f"\nTotal questions tested: {len(test_questions)}")
    print(f"Unique intents found: {len(unique_intents)}")
    print(f"Intents: {unique_intents}")
    
    if len(unique_intents) == 1:
        print("OK All questions mapped to the same intent - GOOD!")
        return True
    else:
        print("WARN Questions mapped to different intents")
        from collections import Counter
        intent_counts = Counter(intents)
        print("\nIntent distribution:")
        for intent, count in intent_counts.items():
            print(f"  {intent}: {count} questions")
        return False

def test_semantic_exam_questions():
    """Test semantically similar questions about exams"""
    print("\n" + "=" * 70)
    print("Testing Semantic Matching: Exam Schedule")
    print("=" * 70)
    
    test_questions = [
        "When are the exams?",
        "Exam schedule",
        "When do exams start?",
        "Examination dates",
        "What is the exam timetable?",
        "When is the final exam?",
        "Exam dates",
        "When are exams happening?",
        "Tell me about exam schedule",
        "What are the exam dates?"
    ]
    
    results = []
    for question in test_questions:
        pred_intent, pred_confidence, pred_response, pred_context = predict_intent(question, return_context=True)
        
        results.append({
            'question': question,
            'intent': pred_intent,
            'confidence': pred_confidence,
            'source': pred_context.get('confidence_source', 'unknown')
        })
        
        print(f"\nQuestion: {question}")
        print(f"  Intent: {pred_intent} ({pred_confidence:.3f}) [{pred_context.get('confidence_source', 'unknown')}]")
    
    # Analyze consistency
    intents = [r['intent'] for r in results]
    unique_intents = set(intents)
    
    print(f"\nTotal questions tested: {len(test_questions)}")
    print(f"Unique intents found: {len(unique_intents)}")
    print(f"Intents: {unique_intents}")
    
    if len(unique_intents) == 1:
        print("OK All questions mapped to the same intent - GOOD!")
        return True
    else:
        print("WARN Questions mapped to different intents")
        from collections import Counter
        intent_counts = Counter(intents)
        print("\nIntent distribution:")
        for intent, count in intent_counts.items():
            print(f"  {intent}: {count} questions")
        return False

def test_confidence_thresholds():
    """Test confidence threshold behavior"""
    print("\n" + "=" * 70)
    print("Testing Confidence Thresholds and Fallback")
    print("=" * 70)
    
    # Test ambiguous questions
    ambiguous_questions = [
        "What should I do?",  # Very ambiguous
        "Tell me something",  # Very ambiguous
        "I need information",  # Vague
        "Help me please",  # Help intent but low confidence
    ]
    
    for question in ambiguous_questions:
        pred_intent, pred_confidence, pred_response, pred_context = predict_intent(question, return_context=True)
        
        print(f"\nQuestion: {question}")
        print(f"  Intent: {pred_intent}")
        print(f"  Confidence: {pred_confidence:.3f}")
        print(f"  Source: {pred_context.get('confidence_source', 'unknown')}")
        print(f"  Response: {pred_response[:100]}...")
        
        if pred_context.get('confidence_source') == 'fallback':
            print("  OK Correctly used fallback for low confidence")
        elif pred_confidence < 0.4:
            print("  WARN Low confidence but didn't use fallback")

if __name__ == '__main__':
    print("Semantic Matching Test Suite")
    print("=" * 70)
    
    try:
        # Test different semantic categories
        library_result = test_semantic_library_questions()
        fee_result = test_semantic_fee_questions()
        exam_result = test_semantic_exam_questions()
        test_confidence_thresholds()
        
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"Library timings consistency: {'PASS' if library_result else 'FAIL'}")
        print(f"Fee structure consistency: {'PASS' if fee_result else 'FAIL'}")
        print(f"Exam schedule consistency: {'PASS' if exam_result else 'FAIL'}")
        
        if library_result and fee_result and exam_result:
            print("\nSUCCESS All semantic matching tests passed!")
            sys.exit(0)
        else:
            print("\nPARTIAL Some semantic matching tests failed. Review the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
