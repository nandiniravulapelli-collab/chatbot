"""
Database Seed Script for University Chatbot
Run this script to populate the MongoDB database with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient
import bcrypt
from datetime import datetime, timedelta
import random

# Database connection
MONGO_URI = 'mongodb://localhost:27017/university_chatbot'

def get_db():
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    return db, client

def clear_collections(db):
    """Clear all existing data"""
    collections = ['users', 'faqs', 'departments', 'fee_structure', 'enrollment_info',
                   'exam_schedule', 'attendance_rules', 'scholarships', 'hostel',
                   'library', 'transport', 'chat_history', 'student_queries']

    for col in collections:
        db[col].delete_many({})
    print("Collections cleared")

def seed_departments(db):
    """Seed departments"""
    departments = [
        {'name': 'Computer Science Engineering', 'code': 'CSE', 'hod': 'Dr. Ramesh Kumar', 'phone': '080-234561', 'email': 'hod.cse@university.edu'},
        {'name': 'Electronics Engineering', 'code': 'ECE', 'hod': 'Dr. Suresh Nair', 'phone': '080-234562', 'email': 'hod.ece@university.edu'},
        {'name': 'Mechanical Engineering', 'code': 'ME', 'hod': 'Dr. Anil Sharma', 'phone': '080-234563', 'email': 'hod.me@university.edu'},
        {'name': 'Civil Engineering', 'code': 'CE', 'hod': 'Dr. Priya Devi', 'phone': '080-234564', 'email': 'hod.ce@university.edu'},
        {'name': 'Electrical Engineering', 'code': 'EEE', 'hod': 'Dr. Vijay Rao', 'phone': '080-234565', 'email': 'hod.eee@university.edu'},
        {'name': 'Information Technology', 'code': 'IT', 'hod': 'Dr. Kavitha N', 'phone': '080-234566', 'email': 'hod.it@university.edu'},
        {'name': 'Business Administration', 'code': 'BBA', 'hod': 'Dr. Meena T', 'phone': '080-234567', 'email': 'hod.bba@university.edu'},
        {'name': 'Computer Applications', 'code': 'MCA', 'hod': 'Dr. Arun K', 'phone': '080-234568', 'email': 'hod.mca@university.edu'}
    ]

    db.departments.insert_many(departments)
    print(f"Inserted {len(departments)} departments")
    return departments

def seed_users(db):
    """Seed users (students and admin)"""
    users = []

    # Admin user
    admin_pass = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users.append({
        'full_name': 'System Administrator',
        'roll_number': 'ADMIN001',
        'department': 'Administration',
        'email': 'admin@university.edu',
        'password': admin_pass,
        'role': 'admin',
        'created_at': datetime.utcnow()
    })

    # Sample students
    departments = ['Computer Science Engineering', 'Electronics Engineering', 'Mechanical Engineering',
                   'Civil Engineering', 'Electrical Engineering', 'Information Technology',
                   'Business Administration', 'Computer Applications']

    student_names = [
        ('Rahul Sharma', '21CS101'), ('Priya Singh', '21CS102'), ('Amit Kumar', '21CS103'),
        ('Sneha Reddy', '21ECE101'), ('Vikram Nair', '21ECE102'), ('Anjali Devi', '21ECE103'),
        ('Suresh Kumar', '21ME101'), ('Kavitha R', '21ME102'), ('Rajesh N', '21ME103'),
        ('Shwetha HS', '21CE101'), ('Manjunath P', '21CE102'), ('Saritha V', '21CE103'),
        ('Vinod Kumar', '22CS201'), ('Divya S', '22CS202'), ('Prakash R', '22CS203'),
        ('Lakshmi M', '22EEE201'), ('Ganesh R', '22EEE202'), ('Nisha P', '22EEE203'),
        ('Krishna K', '22IT201'), ('Sunita R', '22IT202'), ('Mohan S', '22IT203'),
        ('Test Student', 'TEST001')
    ]

    for name, roll in student_names:
        student_pass = bcrypt.hashpw('student123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        dept = random.choice(departments)
        email = f"{roll.lower()}@university.edu" if roll != 'TEST001' else 'student@university.edu'

        users.append({
            'full_name': name,
            'roll_number': roll,
            'department': dept,
            'email': email,
            'password': student_pass,
            'role': 'student',
            'created_at': datetime.utcnow() - timedelta(days=random.randint(30, 365))
        })

    db.users.insert_many(users)
    print(f"Inserted {len(users)} users (1 admin + {len(users)-1} students)")
    return users

def seed_faqs(db):
    """Seed Frequently Asked Questions"""
    faqs = [
        {'question': 'What are the admission requirements?',
         'answer': 'Admission requirements include: 50% aggregate in 10+2 (PCM for engineering courses), valid score in entrance exam (JEE/State level), and personal interview.',
         'category': 'admissions', 'created_at': datetime.utcnow()},

        {'question': 'How do I apply for admission?',
         'answer': 'You can apply online through our university portal. Fill the application form, upload required documents (marksheets, ID proof, photos), pay the application fee of Rs. 500, and submit. You will receive a confirmation email within 48 hours.',
         'category': 'admissions', 'created_at': datetime.utcnow()},

        {'question': 'What is the last date for admission?',
         'answer': 'Admission for the academic year 2024-25 starts on June 1st, 2024 and ends on July 31st, 2024. Late applications may be accepted with a late fee until August 15th.',
         'category': 'admissions', 'created_at': datetime.utcnow()},

        {'question': 'How much is the tuition fee?',
         'answer': 'Tuition fee varies by program: B.Tech - Rs. 1,50,000/year, MBA - Rs. 2,00,000/year, BBA - Rs. 80,000/year, MCA - Rs. 1,20,000/year. Additional fees apply for lab, library, and examination.',
         'category': 'fees', 'created_at': datetime.utcnow()},

        {'question': 'How do I pay my fees?',
         'answer': 'Fees can be paid through the online student portal using credit/debit cards, UPI, net banking, or demand draft drawn in favor of "Smart University". You can also pay at the fee counter (Building A, Room 101) during office hours.',
         'category': 'fees', 'created_at': datetime.utcnow()},

        {'question': 'Can I pay fees in installments?',
         'answer': 'Yes, we offer installment options for tuition fees. You can pay in 2 installments: 50% at the start of semester and 50% mid-semester. A processing fee of Rs. 1,000 applies for installment payments.',
         'category': 'fees', 'created_at': datetime.utcnow()},

        {'question': 'When are the semester exams?',
         'answer': 'End-semester exams are held in November (Fall semester) and May (Spring semester). Mid-semester internal assessments are conducted in September and February respectively. Check the academic calendar for exact dates.',
         'category': 'exams', 'created_at': datetime.utcnow()},

        {'question': 'How do I get my hall ticket?',
         'answer': 'Hall tickets are generated 10 days before exams. Download yours from the student portal under "Examinations > Hall Ticket" after ensuring all fee dues are cleared.',
         'category': 'exams', 'created_at': datetime.utcnow()},

        {'question': 'What is the minimum attendance required?',
         'answer': 'Students must maintain a minimum of 75% attendance in each subject to be eligible for end-semester examinations. Medical leave can exempt up to 10% with proper documentation.',
         'category': 'attendance', 'created_at': datetime.utcnow()},

        {'question': 'What scholarships are available?',
         'answer': 'We offer Merit Scholarship (top 10% students get 50% fee waiver), Sports Scholarship for state/national level players, SC/ST/OBC scholarships as per government norms, and need-based financial aid. Applications open in July.',
         'category': 'scholarships', 'created_at': datetime.utcnow()},

        {'question': 'How do I apply for hostel?',
         'answer': 'Apply for hostel accommodation through the student portal under "Hostel Application". Submit during registration period. Rooms are allotted on merit basis for general and first-come for others. Preference given to students from distant locations.',
         'category': 'hostel', 'created_at': datetime.utcnow()},

        {'question': 'What are the hostel fees?',
         'answer': 'Hostel fee is Rs. 60,000 per year (including mess charges). Separate accommodation for boys and girls with 24/7 security. Rooms are twin-sharing with attached bathrooms. Payment can be done yearly or semester-wise.',
         'category': 'hostel', 'created_at': datetime.utcnow()},

        {'question': 'What are the library timings?',
         'answer': 'Central Library is open Monday-Friday: 8:00 AM to 10:00 PM, Saturday-Sunday: 9:00 AM to 6:00 PM. During exam season, timing extends to midnight.',
         'category': 'library', 'created_at': datetime.utcnow()},

        {'question': 'How many books can I borrow?',
         'answer': 'Students can borrow up to 5 books for 14 days. Overdue fine is Rs. 5 per day per book. SC/ST students get 7 books. Reference books and journals cannot be borrowed.',
         'category': 'library', 'created_at': datetime.utcnow()},

        {'question': 'Is there college transport available?',
         'answer': 'Yes, we operate 25 buses covering major routes across the city. Annual transport fee is Rs. 25,000. Bus passes can be obtained from the transport office. Routes and schedules are available on the student portal.',
         'category': 'transport', 'created_at': datetime.utcnow()},

        {'question': 'How do I get bonafide certificate?',
         'answer': 'Apply for bonafide certificate through the student portal under "Documents Request". It is generated within 3 working days. For urgent needs, visit Admin Block, Room 106 with your ID card.',
         'category': 'documents', 'created_at': datetime.utcnow()},

        {'question': 'Where is the placement cell?',
         'answer': 'The Training and Placement Cell is located in the Main Building, 3rd Floor. Contact: Dr. Sharma (Placement Officer), phone: 080-2345690, email: placements@university.edu.',
         'category': 'placements', 'created_at': datetime.utcnow()},

        {'question': 'What is the CGPA calculation formula?',
         'answer': 'CGPA = Sum of (Grade Points x Credits) / Total Credits. Each grade has a point value: O=10, A+=9, A=8, B+=7, B=6, C=5, P=4, F=0. You need minimum 6.5 CGPA to graduate.',
         'category': 'academics', 'created_at': datetime.utcnow()},

        {'question': 'What facilities are available on campus?',
         'answer': 'Campus facilities include: Central Library, 24/7 WiFi, 3 cafeterias, sports complex (cricket, football, basketball, tennis), modern gym, medical center, ATM, post office, and student activity center.',
         'category': 'facilities', 'created_at': datetime.utcnow()},
    ]

    db.faqs.insert_many(faqs)
    print(f"Inserted {len(faqs)} FAQs")
    return faqs

def seed_fee_structure(db):
    """Seed Fee Structure"""
    fees = []

    departments = [
        ('CSE', 'Computer Science Engineering'),
        ('ECE', 'Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EEE', 'Electrical Engineering'),
        ('IT', 'Information Technology')
    ]

    for code, dept in departments:
        for sem in range(1, 9):
            tuition = 75000 if sem <= 2 else 80000 if sem <= 4 else 85000 if sem <= 6 else 90000
            lab_fee = 5000 if code in ['CSE', 'ECE', 'EEE', 'IT'] else 10000 if code == 'ME' else 3000

            fees.append({
                'department': dept,
                'department_code': code,
                'semester': sem,
                'tuition_fee': tuition,
                'exam_fee': 3000,
                'library_fee': 2000,
                'lab_fee': lab_fee,
                'development_fee': 5000,
                'total': tuition + 3000 + 2000 + lab_fee + 5000,
                'created_at': datetime.utcnow()
            })

    # Add management program fees
    for sem in range(1, 5):
        fees.append({
            'department': 'Business Administration',
            'department_code': 'BBA',
            'semester': sem,
            'tuition_fee': 40000,
            'exam_fee': 2500,
            'library_fee': 1500,
            'lab_fee': 1000,
            'development_fee': 3000,
            'total': 48000,
            'created_at': datetime.utcnow()
        })

    for sem in range(1, 7):
        fees.append({
            'department': 'Computer Applications',
            'department_code': 'MCA',
            'semester': sem,
            'tuition_fee': 60000,
            'exam_fee': 3000,
            'library_fee': 2000,
            'lab_fee': 5000,
            'development_fee': 4000,
            'total': 74000,
            'created_at': datetime.utcnow()
        })

    db.fee_structure.insert_many(fees)
    print(f"Inserted {len(fees)} fee records")

def seed_enrollment(db):
    """Seed Enrollment Information"""
    enrollment_info = [
        {
            'department': 'All Departments',
            'title': 'Fall Semester Enrollment 2024',
            'description': 'Enrollment for all undergraduate and postgraduate programs',
            'start_date': '2024-07-01',
            'end_date': '2024-07-31',
            'requirements': 'Clear all previous dues, Complete course selection online, Submit required documents',
            'late_fee': 500,
            'created_at': datetime.utcnow()
        },
        {
            'department': 'All Departments',
            'title': 'Spring Semester Enrollment 2025',
            'description': 'Enrollment for January 2025 semester',
            'start_date': '2025-01-01',
            'end_date': '2025-01-15',
            'requirements': 'Clear all previous dues, Course selection online',
            'late_fee': 1000,
            'created_at': datetime.utcnow()
        }
    ]

    db.enrollment_info.insert_many(enrollment_info)
    print(f"Inserted {len(enrollment_info)} enrollment records")

def seed_exam_schedule(db):
    """Seed Exam Schedule"""
    exams = [
        {'department': 'All Departments', 'semester': 'Sem 1-8', 'exam_name': 'Mid-Semester Exams (Fall)',
         'start_date': '2024-09-15', 'end_date': '2024-09-25', 'description': 'Internal assessment exams for all programs', 'created_at': datetime.utcnow()},
        {'department': 'All Departments', 'semester': 'Sem 1-8', 'exam_name': 'End-Semester Exams (Fall)',
         'start_date': '2024-11-20', 'end_date': '2024-12-05', 'description': 'Final semester examinations', 'created_at': datetime.utcnow()},
        {'department': 'All Departments', 'semester': 'Sem 1-8', 'exam_name': 'Mid-Semester Exams (Spring)',
         'start_date': '2025-02-15', 'end_date': '2025-02-25', 'description': 'Internal assessment exams', 'created_at': datetime.utcnow()},
        {'department': 'All Departments', 'semester': 'Sem 1-8', 'exam_name': 'End-Semester Exams (Spring)',
         'start_date': '2025-05-10', 'end_date': '2025-05-25', 'description': 'Final semester examinations', 'created_at': datetime.utcnow()},
    ]

    db.exam_schedule.insert_many(exams)
    print(f"Inserted {len(exams)} exam schedules")

def seed_attendance(db):
    """Seed Attendance Rules"""
    rules = {
        'minimum_attendance': 75,
        'medical_leave_exemption': 10,
        'medical_leave_with_documentation': 15,
        'sports_exemption': 5,
        'grading': [
            {'range': '90-100', 'grade': 'O', 'points': 10},
            {'range': '80-89', 'grade': 'A+', 'points': 9},
            {'range': '70-79', 'grade': 'A', 'points': 8},
            {'range': '60-69', 'grade': 'B+', 'points': 7},
            {'range': '50-59', 'grade': 'B', 'points': 6},
            {'range': '40-49', 'grade': 'C', 'points': 5},
        ],
        'attendance_calculation': 'Present days in a subject / Total scheduled classes * 100',
        'policy': 'Students with less than 75% attendance are not eligible for end-semester exams except with special permission',
        'created_at': datetime.utcnow()
    }

    db.attendance_rules.insert_one(rules)
    print("Inserted attendance rules")

def seed_scholarships(db):
    """Seed Scholarship Information"""
    scholarships = [
        {'name': 'Merit Scholarship', 'type': 'Merit', 'amount': '50% tuition waiver', 'eligibility': 'Top 10% students in each program based on CGPA', 'deadline': '2024-08-31', 'description': 'For academically outstanding students maintaining CGPA > 9.0', 'created_at': datetime.utcnow()},
        {'name': 'Sports Excellence Scholarship', 'type': 'Sports', 'amount': '25-100% tuition waiver', 'eligibility': 'State/National level sports participation', 'deadline': '2024-07-31', 'description': 'For students excelling in sports at state or national level', 'created_at': datetime.utcnow()},
        {'name': 'SC/ST Scholarship', 'type': 'Government', 'amount': 'Full tuition + maintenance allowance', 'eligibility': 'SC/ST students as per government norms', 'deadline': '2024-08-15', 'description': 'Government-funded scholarship for SC/ST category students', 'created_at': datetime.utcnow()},
        {'name': 'OBC Scholarship', 'type': 'Government', 'amount': '50% tuition waiver', 'eligibility': 'OBC category with family income < 3 lakhs', 'deadline': '2024-08-15', 'description': 'Government scholarship for OBC category students', 'created_at': datetime.utcnow()},
        {'name': 'Need-based Financial Aid', 'type': 'Need', 'amount': 'Up to 75% tuition waiver', 'eligibility': 'Family annual income < 4 lakhs', 'deadline': '2024-08-31', 'description': 'For students from economically weaker sections', 'created_at': datetime.utcnow()},
        {'name': 'Single Girl Child Scholarship', 'type': 'Special', 'amount': '100% tuition waiver', 'eligibility': 'Only one girl child in the family', 'deadline': '2024-08-31', 'description': 'Special scholarship for single girl child students', 'created_at': datetime.utcnow()},
    ]

    db.scholarships.insert_many(scholarships)
    print(f"Inserted {len(scholarships)} scholarships")

def seed_hostel(db):
    """Seed Hostel Information"""
    hostel_info = [
        {'name': 'Boys Hostel A', 'gender': 'Boys', 'capacity': 500, 'rooms_available': 150, 'room_type': 'Single', 'fee': 70000, 'occupancy': 'Single', 'amenities': 'WiFi, AC, Attached bathroom, Study table, Wardrobe', 'created_at': datetime.utcnow()},
        {'name': 'Boys Hostel B', 'gender': 'Boys', 'capacity': 400, 'rooms_available': 80, 'room_type': 'Twin-sharing', 'fee': 60000, 'occupancy': 'Double', 'amenities': 'WiFi, Fan, Common bathroom, Study hall', 'created_at': datetime.utcnow()},
        {'name': 'Girls Hostel', 'gender': 'Girls', 'capacity': 300, 'rooms_available': 50, 'room_type': 'Twin-sharing', 'fee': 65000, 'occupancy': 'Double', 'amenities': 'WiFi, 24/7 security, Mess, Study room, Common TV room', 'created_at': datetime.utcnow()},
    ]

    db.hostel.insert_many(hostel_info)
    print(f"Inserted {len(hostel_info)} hostel records")

def seed_library(db):
    """Seed Library Information"""
    library_info = {
        'name': 'Central Library',
        'timings': 'Monday-Friday: 8 AM - 10 PM, Saturday-Sunday: 9 AM - 6 PM',
        'timings_exam': 'Open till midnight during exams',
        'max_books': 5,
        'lending_period': 14,
        'renewal_allowed': 2,
        'fine_per_day': 5,
        'max_fine': 500,
        'digital_resources': 'IEEE, Springer, Elsevier, JSTOR',
        'seating_capacity': 500,
        'computers': 50,
        'total_books': 75000,
        'journals': 200,
        'description': 'State-of-the-art library with AC, WiFi, digital resources, and seminar halls',
        'created_at': datetime.utcnow()
    }

    db.library.insert_one(library_info)
    print("Inserted library information")

def seed_transport(db):
    """Seed Transport Information"""
    transport_info = {
        'total_buses': 25,
        'routes': [
            {'route_no': 1, 'route_name': 'City Center', 'stops': ['Railway Station', 'Bus Stand', 'MG Road', 'City Center', 'University'], 'timing': '6:30 AM - 8:30 PM'},
            {'route_no': 2, 'route_name': 'North Zone', 'stops': ['Hebbal', 'Yelahanka', 'Manyata Tech Park', 'University'], 'timing': '6:00 AM - 8:00 PM'},
            {'route_no': 3, 'route_name': 'South Zone', 'stops': ['JP Nagar', 'BTM Layout', 'Electronic City', 'University'], 'timing': '6:00 AM - 8:00 PM'},
            {'route_no': 4, 'route_name': 'East Zone', 'stops': ['Whitefield', 'ITPL', 'Marathahalli', 'University'], 'timing': '6:15 AM - 8:15 PM'},
            {'route_no': 5, 'route_name': 'West Zone', 'stops': ['Kengeri', 'RR Nagar', 'Vijayanagar', 'University'], 'timing': '6:15 AM - 8:15 PM'},
        ],
        'annual_fee': 25000,
        'semester_fee': 14000,
        'rules': 'Bus pass must be carried, Reach pickup point 5 mins early, Report lost pass immediately',
        'contact': 'Transport Office, Building A, Ground Floor',
        'phone': '080-23456700',
        'created_at': datetime.utcnow()
    }

    db.transport.insert_one(transport_info)
    print("Inserted transport information")

def seed_chat_history(db):
    """Seed sample chat history"""
    users = list(db.users.find({'role': 'student'}))

    questions = [
        ('What is the fee structure?', 'fees'),
        ('When are the exams?', 'exams'),
        ('How do I apply for hostel?', 'hostel'),
        ('What scholarships are available?', 'scholarships'),
        ('What are the library timings?', 'library'),
        ('How to get admission?', 'admissions'),
    ]

    if users:
        chat_entries = []
        for _ in range(20):
            user = random.choice(users)
            q, intent = random.choice(questions)
            chat_entries.append({
                'user_id': str(user['_id']),
                'question': q,
                'answer': f'Sample answer for: {q}',
                'intent': intent,
                'confidence': round(random.uniform(0.7, 0.99), 2),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 30))
            })

        db.chat_history.insert_many(chat_entries)
        print(f"Inserted {len(chat_entries)} chat history entries")

def seed_queries(db):
    """Seed sample student queries for admin"""
    users = list(db.users.find({'role': 'student'}))

    queries = [
        'What is the last date for fee payment?',
        'Can I get a fee waiver?',
        'I need to apply for a bonafide certificate',
        'What is my current attendance?',
        'When will results be declared?',
    ]

    query_entries = []
    for _ in range(15):
        if users:
            user = random.choice(users)
            query_entries.append({
                'user_id': str(user['_id']),
                'user_name': user['full_name'],
                'department': user['department'],
                'question': random.choice(queries),
                'intent': random.choice(['fees', 'documents', 'attendance', 'exams', 'general']),
                'status': random.choice(['resolved', 'needs_review']),
                'timestamp': datetime.utcnow() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
            })

    if query_entries:
        db.student_queries.insert_many(query_entries)
        print(f"Inserted {len(query_entries)} student queries")

def main():
    print("=" * 60)
    print("University Chatbot Database Seed Script")
    print("=" * 60)

    print("\nConnecting to MongoDB...")
    db, client = get_db()

    print("\nClearing existing collections...")
    clear_collections(db)

    print("\nSeeding data...")
    print("-" * 40)

    seed_departments(db)
    seed_users(db)
    seed_faqs(db)
    seed_fee_structure(db)
    seed_enrollment(db)
    seed_exam_schedule(db)
    seed_attendance(db)
    seed_scholarships(db)
    seed_hostel(db)
    seed_library(db)
    seed_transport(db)
    seed_chat_history(db)
    seed_queries(db)

    print("-" * 40)
    print("\nDatabase seeding completed successfully!")
    print("\nYou can now login with:")
    print("  Admin    : admin@university.edu / admin123")
    print("  Student  : student@university.edu / student123")
    print("  Test     : test001@university.edu / student123")
    print("\nOr create a new account via the registration page.")
    print("=" * 60)

    client.close()

if __name__ == '__main__':
    main()
