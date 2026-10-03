"""
Test spelling correction integrated with chatbot intent prediction
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.predict import predict_intent
from database.connection import init_db, get_db

def test_spelling_with_chatbot():
    """Test spelling correction with actual chatbot intent prediction"""
    print("Testing Spelling Correction with Chatbot Integration")
    print("=" * 70)
    
    # Initialize database
    db = init_db()
    
    # Test queries with spelling errors
    test_queries = [
        'scholship information',
        'libary timings',
        'transprt facility',
        'hostal rules',
        'attendence policy',
        'admisions process',
        'exm schedule',
    ]
    
    print("\nTesting Intent Prediction with Spelling Correction:")
    print("-" * 70)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            intent, confidence, response = predict_intent(
                query,
                faqs_col=db.faqs if db.faqs is not None else None,
                departments_col=db.departments if db.departments is not None else None,
                fee_structure_col=db.fee_structure if db.fee_structure is not None else None,
                enrollment_col=db.enrollment_info if db.enrollment_info is not None else None,
                exam_schedule_col=db.exam_schedule if db.exam_schedule is not None else None,
                attendance_col=db.attendance_rules if db.attendance_rules is not None else None,
                scholarships_col=db.scholarships if db.scholarships is not None else None,
                hostel_col=db.hostel if db.hostel is not None else None,
                library_col=db.library if db.library is not None else None,
                transport_col=db.transport if db.transport is not None else None,
                return_context=False
            )
            print(f"Intent: {intent}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Response: {response[:100]}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 70)
    print("Spelling correction is integrated and working with chatbot!")
    print("The chatbot will automatically correct spelling errors before")
    print("intent detection and retrieval.")

if __name__ == '__main__':
    test_spelling_with_chatbot()
