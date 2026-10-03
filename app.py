from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
import bcrypt
import json
from datetime import datetime
from bson import ObjectId
from config import Config
from database.connection import init_db, get_db, close_db
from ml.predict import predict_intent
from ml.nlg_generator import get_nlg_generator

app = Flask(__name__)
app.config.from_object(Config)

# User roles collection
users_col = None
faqs_col = None
chat_history_col = None
departments_col = None
fee_structure_col = None
enrollment_col = None
exam_schedule_col = None
attendance_col = None
scholarships_col = None
hostel_col = None
library_col = None
transport_col = None
queries_col = None
contact_details_col = None
student_messages_col = None

@app.before_request
def before_request():
    db = get_db()
    global users_col, faqs_col, chat_history_col, departments_col
    global fee_structure_col, enrollment_col, exam_schedule_col, attendance_col
    global scholarships_col, hostel_col, library_col, transport_col, queries_col
    global contact_details_col, student_messages_col

    users_col = db.users
    faqs_col = db.faqs
    chat_history_col = db.chat_history
    departments_col = db.departments
    fee_structure_col = db.fee_structure
    enrollment_col = db.enrollment_info
    exam_schedule_col = db.exam_schedule
    attendance_col = db.attendance_rules
    scholarships_col = db.scholarships
    hostel_col = db.hostel
    library_col = db.library
    transport_col = db.transport
    queries_col = db.student_queries
    contact_details_col = db.contact_details
    student_messages_col = db.student_messages

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Login required'}), 401
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Login required'}), 401
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============ PAGE ROUTES ============

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')

        user = users_col.find_one({'email': email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session.permanent = True
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['name'] = user['full_name']
            session['role'] = user.get('role', 'student')
            session['roll_number'] = user.get('roll_number', '')
            session['department'] = user.get('department', '')

            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'redirect': url_for('admin_dashboard') if user.get('role') == 'admin' else url_for('student_dashboard')
                })
            return redirect(url_for('admin_dashboard') if user.get('role') == 'admin' else url_for('student_dashboard'))

        if request.is_json:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
        flash('Invalid email or password', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        full_name = data.get('full_name')
        roll_number = data.get('roll_number')
        department = data.get('department')
        email = data.get('email')
        password = data.get('password')

        # Check if user exists
        if users_col.find_one({'email': email}):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        if users_col.find_one({'roll_number': roll_number}):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Roll number already registered'}), 400
            flash('Roll number already registered', 'error')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = {
            'full_name': full_name,
            'roll_number': roll_number,
            'department': department,
            'email': email,
            'password': hashed_password,
            'role': 'student',
            'created_at': datetime.utcnow()
        }

        result = users_col.insert_one(user)

        if request.is_json:
            return jsonify({'success': True, 'message': 'Registration successful', 'redirect': url_for('login')})
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('login'))

    departments = list(departments_col.find({}, {'name': 1}))
    return render_template('register.html', departments=departments)

@app.route('/dashboard')
@login_required
def student_dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chat.html')

@app.route('/profile')
@login_required
def profile():
    user = users_col.find_one({'email': session.get('email')})
    return render_template('profile.html', user=user)

@app.route('/faq')
def faq():
    faqs = list(faqs_col.find({}).sort('created_at', -1))
    return render_template('faq.html', faqs=faqs)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

# ============ API ROUTES ============

@app.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    user = users_col.find_one({'email': session.get('email')}, {'password': 0})
    if user:
        user['_id'] = str(user['_id'])
        return jsonify({'success': True, 'user': user})
    return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()

    user = users_col.find_one({'email': session.get('email')})
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    if data.get('password'):
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        data['password'] = hashed_password

    users_col.update_one({'email': session.get('email')}, {'$set': data})
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
        return jsonify({'success': False, 'message': 'Question is required'}), 400

    # Get conversation history for context (last 5 exchanges)
    user_id = session.get('user_id')
    conversation_history = list(chat_history_col.find(
        {'user_id': user_id},
        {'question': 1, 'answer': 1}
    ).sort('timestamp', -1).limit(5))
    conversation_history.reverse()  # Get in chronological order
    
    # Convert ObjectId to string for JSON serialization
    for entry in conversation_history:
        entry['_id'] = str(entry['_id'])

    # Predict intent using ML and get context
    intent, confidence, response, context = predict_intent(
        question, faqs_col, departments_col,
        fee_structure_col, enrollment_col, exam_schedule_col,
        attendance_col, scholarships_col, hostel_col,
        library_col, transport_col, return_context=True
    )

    # Try to generate natural response using NLG
    nlg_generator = get_nlg_generator()
    nlg_response = None
    
    if nlg_generator and nlg_generator.is_available():
        try:
            nlg_response = nlg_generator.generate_response(
                question=question,
                context=context,
                conversation_history=conversation_history
            )
        except Exception as e:
            print(f"NLG generation failed: {e}")
    
    # Use NLG response if available, otherwise fall back to original response
    final_response = nlg_response if nlg_response else response
    response_source = 'nlg' if nlg_response else 'faq'

    # Calculate display confidence (capped at 95% to avoid false 100% matches)
    display_confidence = min(float(confidence) * 100, 95.0)
    
    # Adjust confidence based on source for better user feedback
    if response_source == 'nlg':
        # NLG responses get slight confidence boost
        display_confidence = min(display_confidence + 5, 95.0)
    elif response_source == 'faq' and context.get('confidence_source') == 'fallback':
        # Fallback responses have low confidence
        display_confidence = max(display_confidence, 30.0)

    # Save chat history
    chat_entry = {
        'user_id': session.get('user_id'),
        'question': question,
        'answer': final_response,
        'intent': intent,
        'confidence': float(confidence),
        'display_confidence': round(display_confidence, 1),
        'response_source': response_source,
        'confidence_source': context.get('confidence_source', 'unknown') if context else 'unknown',
        'timestamp': datetime.utcnow()
    }
    chat_history_col.insert_one(chat_entry)

    # Save query for admin review
    queries_col.insert_one({
        'user_id': session.get('user_id'),
        'user_name': session.get('name'),
        'department': session.get('department'),
        'question': question,
        'intent': intent,
        'status': 'resolved' if confidence > 0.5 else 'needs_review',
        'response_source': response_source,
        'timestamp': datetime.utcnow()
    })

    return jsonify({
        'success': True,
        'response': final_response,
        'intent': intent,
        'confidence': float(confidence),
        'display_confidence': round(display_confidence, 1),
        'response_source': response_source,
        'confidence_source': context.get('confidence_source', 'unknown') if context else 'unknown'
    })

@app.route('/api/chat/history', methods=['GET'])
@login_required
def get_chat_history():
    user_id = session.get('user_id')
    search = request.args.get('search', '')

    query = {'user_id': user_id}
    if search:
        query['question'] = {'$regex': search, '$options': 'i'}

    history = list(chat_history_col.find(query).sort('timestamp', -1).limit(100))

    for entry in history:
        entry['_id'] = str(entry['_id'])
        entry['timestamp'] = entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    return jsonify({'success': True, 'history': history})

@app.route('/api/chat/history/<history_id>', methods=['DELETE'])
@login_required
def delete_chat_history(history_id):
    from bson.objectid import ObjectId
    result = chat_history_col.delete_one({'_id': ObjectId(history_id), 'user_id': session.get('user_id')})
    if result.deleted_count:
        return jsonify({'success': True, 'message': 'Chat history deleted'})
    return jsonify({'success': False, 'message': 'Chat history not found'}), 404

@app.route('/api/chat/history/clear', methods=['DELETE'])
@login_required
def clear_chat_history():
    chat_history_col.delete_many({'user_id': session.get('user_id')})
    return jsonify({'success': True, 'message': 'Chat history cleared'})

# ========== ADMIN API ROUTES ==========

@app.route('/api/admin/faqs', methods=['GET'])
@admin_required
def get_faqs():
    faqs = list(faqs_col.find({}).sort('created_at', -1))
    for faq in faqs:
        faq['_id'] = str(faq['_id'])
    return jsonify({'success': True, 'faqs': faqs})

@app.route('/api/admin/faqs', methods=['POST'])
@admin_required
def add_faq():
    try:
        data = request.get_json()
        if not data or not data.get('question') or not data.get('answer'):
            return jsonify({'success': False, 'message': 'Question and answer are required'}), 400
        
        faq = {
            'question': data.get('question'),
            'answer': data.get('answer'),
            'category': data.get('category', 'general'),
            'created_at': datetime.utcnow()
        }
        result = faqs_col.insert_one(faq)
        faq['_id'] = str(result.inserted_id)
        print(f"FAQ added successfully: {faq['question']}")
        return jsonify({'success': True, 'message': 'FAQ added', 'faq': faq})
    except Exception as e:
        print(f"Error adding FAQ: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error adding FAQ: {str(e)}'}), 500

@app.route('/api/admin/faqs/<faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    from bson.objectid import ObjectId
    data = request.get_json()
    faqs_col.update_one({'_id': ObjectId(faq_id)}, {'$set': {
        'question': data.get('question'),
        'answer': data.get('answer'),
        'category': data.get('category', 'general'),
        'updated_at': datetime.utcnow()
    }})
    return jsonify({'success': True, 'message': 'FAQ updated'})

@app.route('/api/admin/faqs/<faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    from bson.objectid import ObjectId
    faqs_col.delete_one({'_id': ObjectId(faq_id)})
    return jsonify({'success': True, 'message': 'FAQ deleted'})

@app.route('/api/admin/students', methods=['GET'])
@admin_required
def get_students():
    students = list(users_col.find({'role': 'student'}, {'password': 0}))
    for student in students:
        student['_id'] = str(student['_id'])
    return jsonify({'success': True, 'students': students})

@app.route('/api/admin/students/<student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    from bson.objectid import ObjectId
    users_col.delete_one({'_id': ObjectId(student_id), 'role': 'student'})
    return jsonify({'success': True, 'message': 'Student deleted'})

@app.route('/api/admin/queries', methods=['GET'])
@admin_required
def get_queries():
    queries = list(queries_col.find({}).sort('timestamp', -1).limit(100))
    for q in queries:
        q['_id'] = str(q['_id'])
        q['timestamp'] = q['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({'success': True, 'queries': queries})

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def get_analytics():
    try:
        total_students = users_col.count_documents({'role': 'student'})
        total_faqs = faqs_col.count_documents({})
        total_queries = queries_col.count_documents({})
        resolved_queries = queries_col.count_documents({'status': 'resolved'})

        # Intent distribution
        pipeline = [
            {'$group': {'_id': '$intent', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        intent_stats = list(chat_history_col.aggregate(pipeline))

        return jsonify({
            'success': True,
            'analytics': {
                'total_students': total_students,
                'total_faqs': total_faqs,
                'total_queries': total_queries,
                'resolved_queries': resolved_queries,
                'intent_distribution': intent_stats
            }
        })
    except Exception as e:
        print(f"Error getting analytics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error loading analytics: {str(e)}',
            'analytics': {
                'total_students': 0,
                'total_faqs': 0,
                'total_queries': 0,
                'resolved_queries': 0,
                'intent_distribution': []
            }
        }), 500

@app.route('/api/admin/fees', methods=['POST'])
@admin_required
def add_fee():
    try:
        data = request.get_json()
        fee = {
            'department': data.get('department'),
            'semester': data.get('semester'),
            'tuition_fee': data.get('tuition_fee'),
            'exam_fee': data.get('exam_fee'),
            'library_fee': data.get('library_fee'),
            'lab_fee': data.get('lab_fee'),
            'total': data.get('total'),
            'created_at': datetime.utcnow()
        }
        result = fee_structure_col.insert_one(fee)
        fee['_id'] = str(result.inserted_id)
        print(f"Fee structure added: {fee['department']} - Semester {fee['semester']}")
        return jsonify({'success': True, 'message': 'Fee structure added', 'fee': fee})
    except Exception as e:
        print(f"Error adding fee: {e}")
        return jsonify({'success': False, 'message': f'Error adding fee: {str(e)}'}), 500

@app.route('/api/admin/fees', methods=['GET'])
@admin_required
def get_fees():
    try:
        fees = list(fee_structure_col.find({}).sort('created_at', -1))
        for fee in fees:
            fee['_id'] = str(fee['_id'])
        return jsonify({'success': True, 'fees': fees})
    except Exception as e:
        print(f"Error getting fees: {e}")
        return jsonify({'success': False, 'message': f'Error getting fees: {str(e)}'}), 500

@app.route('/api/admin/fees/<fee_id>', methods=['DELETE'])
@admin_required
def delete_fee(fee_id):
    try:
        from bson.objectid import ObjectId
        fee_structure_col.delete_one({'_id': ObjectId(fee_id)})
        return jsonify({'success': True, 'message': 'Fee structure deleted'})
    except Exception as e:
        print(f"Error deleting fee: {e}")
        return jsonify({'success': False, 'message': f'Error deleting fee: {str(e)}'}), 500

@app.route('/api/admin/enrollment', methods=['POST'])
@admin_required
def add_enrollment():
    data = request.get_json()
    enrollment = {
        'department': data.get('department'),
        'title': data.get('title'),
        'description': data.get('description'),
        'start_date': data.get('start_date'),
        'end_date': data.get('end_date'),
        'requirements': data.get('requirements'),
        'created_at': datetime.utcnow()
    }
    enrollment_col.insert_one(enrollment)
    return jsonify({'success': True, 'message': 'Enrollment information added'})

@app.route('/api/admin/exams', methods=['POST'])
@admin_required
def add_exam():
    try:
        data = request.get_json()
        exam = {
            'department': data.get('department'),
            'semester': data.get('semester'),
            'exam_name': data.get('exam_name'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'description': data.get('description'),
            'created_at': datetime.utcnow()
        }
        result = exam_schedule_col.insert_one(exam)
        exam['_id'] = str(result.inserted_id)
        print(f"Exam schedule added: {exam['exam_name']}")
        return jsonify({'success': True, 'message': 'Exam schedule added', 'exam': exam})
    except Exception as e:
        print(f"Error adding exam: {e}")
        return jsonify({'success': False, 'message': f'Error adding exam: {str(e)}'}), 500

@app.route('/api/admin/exams', methods=['GET'])
@admin_required
def get_exams():
    try:
        exams = list(exam_schedule_col.find({}).sort('created_at', -1))
        for exam in exams:
            exam['_id'] = str(exam['_id'])
        return jsonify({'success': True, 'exams': exams})
    except Exception as e:
        print(f"Error getting exams: {e}")
        return jsonify({'success': False, 'message': f'Error getting exams: {str(e)}'}), 500

@app.route('/api/admin/exams/<exam_id>', methods=['DELETE'])
@admin_required
def delete_exam(exam_id):
    try:
        from bson.objectid import ObjectId
        exam_schedule_col.delete_one({'_id': ObjectId(exam_id)})
        return jsonify({'success': True, 'message': 'Exam schedule deleted'})
    except Exception as e:
        print(f"Error deleting exam: {e}")
        return jsonify({'success': False, 'message': f'Error deleting exam: {str(e)}'}), 500

# Student-accessible endpoints for fees and exams
@app.route('/api/fees', methods=['GET'])
@login_required
def get_student_fees():
    try:
        # Get all fee structures (students can see all departments for reference)
        fees = list(fee_structure_col.find({}).sort('created_at', -1))
        for fee in fees:
            fee['_id'] = str(fee['_id'])
        return jsonify({'success': True, 'fees': fees})
    except Exception as e:
        print(f"Error getting student fees: {e}")
        return jsonify({'success': False, 'message': f'Error getting fees: {str(e)}'}), 500

@app.route('/api/exams', methods=['GET'])
@login_required
def get_student_exams():
    try:
        # Get all exam schedules (students can see all departments for reference)
        exams = list(exam_schedule_col.find({}).sort('created_at', -1))
        for exam in exams:
            exam['_id'] = str(exam['_id'])
        return jsonify({'success': True, 'exams': exams})
    except Exception as e:
        print(f"Error getting student exams: {e}")
        return jsonify({'success': False, 'message': f'Error getting exams: {str(e)}'}), 500

# Contact Details API (Admin can edit)
@app.route('/api/contact-details', methods=['GET'])
def get_contact_details():
    try:
        details = contact_details_col.find_one({})
        if not details:
            # Initialize default contact details
            default_details = {
                'address': 'University Campus\nEducation Road, Main Building\nCity - 560001',
                'phone': 'Toll Free: 1800-123-4567\nOffice: +91 80 2345 6789\nFax: +91 80 2345 6790',
                'email': 'General: info@university.edu\nAdmissions: admit@university.edu\nSupport: help@university.edu',
                'office_hours': 'Monday - Friday: 9:00 AM - 5:00 PM\nSaturday: 9:00 AM - 1:00 PM\nSunday: Closed'
            }
            contact_details_col.insert_one(default_details)
            details = default_details
        details['_id'] = str(details['_id'])
        return jsonify({'success': True, 'details': details})
    except Exception as e:
        print(f"Error getting contact details: {e}")
        return jsonify({'success': False, 'message': f'Error getting contact details: {str(e)}'}), 500

@app.route('/api/admin/contact-details', methods=['PUT'])
@login_required
def update_contact_details():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    try:
        data = request.json
        contact_details_col.update_one({}, {'$set': data}, upsert=True)
        return jsonify({'success': True, 'message': 'Contact details updated successfully'})
    except Exception as e:
        print(f"Error updating contact details: {e}")
        return jsonify({'success': False, 'message': f'Error updating contact details: {str(e)}'}), 500

# Student Messages API
@app.route('/api/student-messages', methods=['POST'])
@login_required
def send_student_message():
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': 'Only students can send messages'}), 403
    try:
        data = request.json
        message = {
            'student_id': session.get('user_id'),
            'student_name': session.get('name'),
            'student_email': session.get('email'),
            'subject': data.get('subject'),
            'message': data.get('message'),
            'reply': None,
            'status': 'pending',
            'created_at': datetime.now(),
            'replied_at': None
        }
        student_messages_col.insert_one(message)
        return jsonify({'success': True, 'message': 'Message sent successfully'})
    except Exception as e:
        print(f"Error sending student message: {e}")
        return jsonify({'success': False, 'message': f'Error sending message: {str(e)}'}), 500

@app.route('/api/admin/student-messages', methods=['GET'])
@login_required
def get_student_messages():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    try:
        messages = list(student_messages_col.find({}).sort('created_at', -1))
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            if msg.get('created_at'):
                msg['created_at'] = msg['created_at'].isoformat()
            if msg.get('replied_at'):
                msg['replied_at'] = msg['replied_at'].isoformat()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        print(f"Error getting student messages: {e}")
        return jsonify({'success': False, 'message': f'Error getting messages: {str(e)}'}), 500

@app.route('/api/admin/student-messages/<message_id>/reply', methods=['PUT'])
@login_required
def reply_student_message(message_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    try:
        data = request.json
        reply = data.get('reply')
        student_messages_col.update_one(
            {'_id': ObjectId(message_id)},
            {
                '$set': {
                    'reply': reply,
                    'status': 'replied',
                    'replied_at': datetime.now()
                }
            }
        )
        return jsonify({'success': True, 'message': 'Reply sent successfully'})
    except Exception as e:
        print(f"Error replying to student message: {e}")
        return jsonify({'success': False, 'message': f'Error sending reply: {str(e)}'}), 500

@app.route('/api/student-messages', methods=['GET'])
@login_required
def get_my_messages():
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    try:
        messages = list(student_messages_col.find({'student_id': session.get('user_id')}).sort('created_at', -1))
        for msg in messages:
            msg['_id'] = str(msg['_id'])
            if msg.get('created_at'):
                msg['created_at'] = msg['created_at'].isoformat()
            if msg.get('replied_at'):
                msg['replied_at'] = msg['replied_at'].isoformat()
        return jsonify({'success': True, 'messages': messages})
    except Exception as e:
        print(f"Error getting my messages: {e}")
        return jsonify({'success': False, 'message': f'Error getting messages: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
