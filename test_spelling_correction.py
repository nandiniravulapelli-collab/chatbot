"""
Test script for spelling correction feature
Tests the examples provided by the user
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.spelling_corrector import SpellingCorrector

def run_spelling_correction_tests():
    """Test spelling correction with provided examples"""
    print("Testing Spelling Correction Feature")
    print("=" * 70)
    
    corrector = SpellingCorrector()
    
    # Test cases from user requirements
    test_cases = [
        ('scholship', 'scholarship'),
        ('libary', 'library'),
        ('transprt', 'transport'),
        ('hostal', 'hostel'),
        ('attendence', 'attendance'),
        ('admisions', 'admissions'),
        ('exm', 'exam'),
    ]
    
    print("\nSingle Word Tests:")
    print("-" * 70)
    all_passed = True
    
    for original, expected in test_cases:
        corrected = corrector.correct_word(original)
        passed = corrected == expected
        status = "PASS" if passed else "FAIL"
        print(f"{status}: '{original}' -> '{corrected}' (expected: '{expected}')")
        if not passed:
            all_passed = False
    
    # Test full queries with typos in ANY word
    print("\nFull Query Tests (typos in any word):")
    print("-" * 70)
    
    query_tests = [
        'What is the scholship amount?',
        'libary timings please',
        'transprt routes available',
        'hostal room booking',
        'attendence percentage required',
        'admisions last date',
        'exm schedule for CSE',
        'scholship for SC students',
        'libary book return policy',
        'transprt fee structure',
        'computr science department',
        'enginering courses',
        'departmet of CSE',
        'universiti information',
        'colleg campus',
        'studen portal',
        'faculti members',
        'administratn office',
        'enrollmet process',
        'registratin deadline',
        'eligiblity criteria',
        'documnt requirements',
        'applicatin form',
        'certifcate verification',
        'diploma programs',
        'curriculm details',
        'syllabus for semestr',
        'academic calndar',
        'lectur schedule',
        'practical class timing',
        'laboratory facilitis',
        'examnation dates',
        'result announcment',
        'placement opportnities',
        'career guidnce',
        'hostel accomodation',
        'transporttion service',
        'library resorces',
        'attndance policy',
        'fee paymnt options',
        'scholarship applicaton',
        'student asistance',
        'technical support',
        'general inquiri',
    ]
    
    for query in query_tests:
        corrected = corrector.correct_query(query)
        corrections = corrector.get_corrections_made(query, corrected)
        print(f"\nOriginal:  {query}")
        print(f"Corrected: {corrected}")
        if corrections:
            print(f"Changes:   {corrections}")
        else:
            print("Changes:   None (no correction needed)")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("All single word tests PASSED")
    else:
        print("Some single word tests FAILED")
    
    return all_passed

if __name__ == '__main__':
    success = run_spelling_correction_tests()
    sys.exit(0 if success else 1)
