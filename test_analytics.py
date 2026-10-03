"""
Test script to verify analytics endpoint and data persistence
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_db, get_db
from datetime import datetime

def test_analytics_data():
    """Test if analytics data is being properly stored and retrieved"""
    print("Testing Analytics Data Persistence")
    print("=" * 50)
    
    try:
        # Initialize database connection
        db = init_db()
        
        # Check collections
        users_col = db.users
        faqs_col = db.faqs
        queries_col = db.student_queries
        chat_history_col = db.chat_history
        fee_structure_col = db.fee_structure
        exam_schedule_col = db.exam_schedule
        
        # Count documents
        total_students = users_col.count_documents({'role': 'student'})
        total_faqs = faqs_col.count_documents({})
        total_queries = queries_col.count_documents({})
        resolved_queries = queries_col.count_documents({'status': 'resolved'})
        
        print(f"Total Students: {total_students}")
        print(f"Total FAQs: {total_faqs}")
        print(f"Total Queries: {total_queries}")
        print(f"Resolved Queries: {resolved_queries}")
        
        # Add a test FAQ if none exist
        if total_faqs == 0:
            print("\nNo FAQs found. Adding a test FAQ...")
            test_faq = {
                'question': 'What is the test question?',
                'answer': 'This is a test answer.',
                'category': 'general',
                'created_at': datetime.utcnow()
            }
            result = faqs_col.insert_one(test_faq)
            print(f"Test FAQ added with ID: {result.inserted_id}")
            
            # Verify it was added
            new_total_faqs = faqs_col.count_documents({})
            print(f"Total FAQs after adding: {new_total_faqs}")
        
        # Add a test query if none exist
        if total_queries == 0:
            print("\nNo queries found. Adding a test query...")
            test_query = {
                'user_id': 'test_user',
                'user_name': 'Test User',
                'department': 'CSE',
                'question': 'Test question',
                'intent': 'test',
                'status': 'resolved',
                'timestamp': datetime.utcnow()
            }
            result = queries_col.insert_one(test_query)
            print(f"Test query added with ID: {result.inserted_id}")
            
            # Verify it was added
            new_total_queries = queries_col.count_documents({})
            print(f"Total queries after adding: {new_total_queries}")
        
        # Check fee structure and exam schedule collections
        print("\nChecking fee structure and exam schedule collections...")
        fee_count = fee_structure_col.count_documents({})
        exam_count = exam_schedule_col.count_documents({})
        print(f"Fee structure records: {fee_count}")
        print(f"Exam schedule records: {exam_count}")
        
        # Add test fee structure if none exist
        if fee_count == 0:
            print("No fee structures found. Adding a test fee structure...")
            test_fee = {
                'department': 'CSE',
                'semester': 1,
                'tuition_fee': 50000,
                'exam_fee': 5000,
                'library_fee': 2000,
                'lab_fee': 3000,
                'total': 60000,
                'created_at': datetime.utcnow()
            }
            result = fee_structure_col.insert_one(test_fee)
            print(f"Test fee structure added with ID: {result.inserted_id}")
        
        # Add test exam schedule if none exist
        if exam_count == 0:
            print("No exam schedules found. Adding a test exam schedule...")
            test_exam = {
                'department': 'CSE',
                'semester': 1,
                'exam_name': 'Mid Semester Examination',
                'start_date': '2024-03-15',
                'end_date': '2024-03-30',
                'description': 'Regular mid-semester examinations for all subjects',
                'created_at': datetime.utcnow()
            }
            result = exam_schedule_col.insert_one(test_exam)
            print(f"Test exam schedule added with ID: {result.inserted_id}")
        
        # Test analytics aggregation
        print("\nTesting analytics aggregation...")
        pipeline = [
            {'$group': {'_id': '$intent', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        intent_stats = list(chat_history_col.aggregate(pipeline))
        print(f"Intent distribution: {intent_stats}")
        
        print("\nOK Analytics data test completed successfully")
        return True
        
    except Exception as e:
        print(f"\nERROR Error during analytics test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_analytics_data()
    sys.exit(0 if success else 1)
