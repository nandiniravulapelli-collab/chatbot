"""
Test script to verify student-accessible API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import init_db, get_db

def test_student_apis():
    """Test if student-accessible API endpoints work"""
    print("Testing Student API Endpoints")
    print("=" * 50)
    
    try:
        # Initialize database connection
        db = init_db()
        
        # Test collections
        fee_structure_col = db.fee_structure
        exam_schedule_col = db.exam_schedule
        
        # Get sample data
        fees = list(fee_structure_col.find({}).limit(3))
        exams = list(exam_schedule_col.find({}).limit(3))
        
        print(f"Fee structure sample data:")
        for fee in fees:
            print(f"  - {fee.get('department')} Sem {fee.get('semester')}: Rs. {fee.get('total')}")
        
        print(f"\nExam schedule sample data:")
        for exam in exams:
            print(f"  - {exam.get('exam_name')}: {exam.get('start_date')} to {exam.get('end_date')}")
        
        print("\nOK Student API data test completed successfully")
        return True
        
    except Exception as e:
        print(f"\nERROR Error during student API test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_student_apis()
    sys.exit(0 if success else 1)
