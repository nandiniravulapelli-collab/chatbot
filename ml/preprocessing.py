import nltk
import json
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet, stopwords
import pickle
import os
import re

# Download required NLTK data
def download_nltk_data():
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

download_nltk_data()

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Custom stopwords to remove (words that might be important for intent detection)
custom_keep_words = {'what', 'when', 'where', 'which', 'who', 'how', 'can', 'could', 'should', 'need', 'want'}

# Update stopwords
custom_stopwords = stop_words - custom_keep_words

# Synonyms for common words - maps variations to canonical forms
SYNONYMS = {
    # Admission related
    'admit': 'admission',
    'admissions': 'admission',
    'apply': 'admission',
    'enroll': 'enrollment',
    'register': 'enrollment',
    'registration': 'enrollment',
    'join': 'admission',
    'enter': 'admission',

    # Fee related
    'fee': 'fees',
    'cost': 'fees',
    'price': 'fees',
    'payment': 'fees',
    'charges': 'fees',
    'amount': 'fees',
    'money': 'fees',
    'tuition': 'fees',

    # Exam related
    'exam': 'exams',
    'examination': 'exams',
    'test': 'exams',
    'tests': 'exams',
    'testing': 'exams',

    # Library related
    'libraries': 'library',
    'book': 'library',
    'books': 'library',

    # Hostel related
    'hostels': 'hostel',
    'dorm': 'hostel',
    'dorms': 'hostel',
    'dormitory': 'hostel',
    'accommodation': 'hostel',
    'housing': 'hostel',
    'room': 'hostel',
    'rooms': 'hostel',
    'stay': 'hostel',

    # Transport related
    'transport': 'transport',
    'transportation': 'transport',
    'bus': 'transport',
    'buses': 'transport',
    'shuttle': 'transport',
    'vehicle': 'transport',

    # Scholarship related
    'scholarship': 'scholarships',
    'scholar': 'scholarships',
    'financial aid': 'scholarships',
    'aid': 'scholarships',
    'funding': 'scholarships',
    'grant': 'scholarships',

    # Attendance related
    'attend': 'attendance',
    'attending': 'attendance',
    'present': 'attendance',
    'absent': 'attendance',

    # Campus related
    'campus': 'facilities',
    'facility': 'facilities',
    'amenities': 'facilities',
    'infrastructure': 'facilities',

    # Faculty related
    'teacher': 'faculty',
    'teachers': 'faculty',
    'professor': 'faculty',
    'professors': 'faculty',
    'lecturer': 'faculty',
    'staff': 'faculty',

    # Course related
    'course': 'courses',
    'class': 'courses',
    'classes': 'courses',
    'subject': 'courses',
    'subjects': 'courses',
    'program': 'courses',
    'programs': 'courses',
    'degree': 'courses',

    # Schedule related
    'schedule': 'timetable',
    'timings': 'timetable',
    'time': 'timetable',
    'hours': 'timetable',
    'period': 'timetable',

    # Help related
    'assist': 'help',
    'assistance': 'help',
    'support': 'help',
    'guide': 'help',

    # Contact related
    'contact': 'contact',
    'reach': 'contact',
    'phone': 'contact',
    'email': 'contact',
    'call': 'contact',

    # Document related
    'certificate': 'documents',
    'certificates': 'documents',
    'document': 'documents',
    'docs': 'documents',
    'paper': 'documents',
    'papers': 'documents',
    'bonafide': 'documents',
    'id': 'documents',

    # Placement related
    'placement': 'placements',
    'placements': 'placements',
    'job': 'placements',
    'jobs': 'placements',
    'career': 'placements',
    'employment': 'placements',
    'recruitment': 'placements',
    'company': 'placements',
    'companies': 'placements',

    # Sports related
    'sport': 'sports',
    'sporting': 'sports',
    'game': 'sports',
    'games': 'sports',
    'athletics': 'sports',
    'gym': 'sports',
    'fitness': 'sports',

    # Food related
    'food': 'cafeteria',
    'canteen': 'cafeteria',
    'cafeteria': 'cafeteria',
    'cafeterias': 'cafeteria',
    'mess': 'cafeteria',
    'dining': 'cafeteria',
    'eat': 'cafeteria',
    'restaurant': 'cafeteria',

    # Greeting synonyms
    'hi': 'greeting',
    'hello': 'greeting',
    'hey': 'greeting',
    'hola': 'greeting',
    'howdy': 'greeting',
    'greetings': 'greeting',
    'morning': 'greeting',
    'afternoon': 'greeting',
    'evening': 'greeting',

    # Goodbye synonyms
    'bye': 'goodbye',
    'goodbye': 'goodbye',
    'later': 'goodbye',
    'cya': 'goodbye',
    'see': 'goodbye',
    'leave': 'goodbye',

    # Thanks synonyms
    'thanks': 'thanks',
    'thank': 'thanks',
    'thankyou': 'thanks',
    'appreciate': 'thanks',
    'grateful': 'thanks',

    # Query synonyms
    'available': 'available',
    'availability': 'available',
    'offer': 'available',
    'offers': 'available',
    'provide': 'available',
    'provides': 'available',

    # Info related
    'info': 'information',
    'information': 'information',
    'details': 'information',
    'detail': 'information',
    'about': 'information',
    'tell': 'information',

    # Requirement related
    'require': 'requirements',
    'requirements': 'requirements',
    'required': 'requirements',
    'requirement': 'requirements',
    'need': 'requirements',
    'needs': 'requirements',
    'criteria': 'requirements',
    'eligibility': 'requirements',
    'eligible': 'requirements',
}

# Intent dataset for training with more patterns
INTENTS = {
    "intents": [
        {
            "tag": "greeting",
            "patterns": [
                "Hi", "Hello", "Hey there", "Good morning", "Good afternoon", "Good evening",
                "Howdy", "What's up", "Greetings", "Hi there", "Hello there", "Hey",
                "Good day", "How are you", "How do you do", "Nice to meet you",
                "Hi bot", "Hello bot", "Hey bot", "Greetings bot", "Hello assistant",
                "Hi assistant", "Hey assistant", "Good morning bot", "Hi there bot",
                "Hello anyone there", "Hi anyone", "Is anyone there", "Is someone there"
            ],
            "responses": [
                "Hello! Welcome to University Assistant. How can I help you today?",
                "Hi there! I'm your university chatbot. What would you like to know?",
                "Welcome! I'm here to assist you with university-related queries."
            ]
        },
        {
            "tag": "goodbye",
            "patterns": [
                "Bye", "Goodbye", "See you later", "Take care", "See ya", "Catch you later",
                "Have a good day", "Until next time", "Bye bye", "Good night", "See you",
                "I'm leaving", "Gotta go", "Talk to you later", "Have to go",
                "Leaving now", "Goodbye bot", "Bye bot", "See you soon", "Till next time"
            ],
            "responses": [
                "Goodbye! Feel free to come back anytime.",
                "Take care! Have a great day!",
                "Bye! Don't hesitate to ask if you have more questions."
            ]
        },
        {
            "tag": "thanks",
            "patterns": [
                "Thanks", "Thank you", "Thanks a lot", "Thank you so much", "Appreciate it",
                "Many thanks", "Great help", "You're a lifesaver", "Thank you very much",
                "Thanks for help", "Thanks for helping", "Appreciate your help",
                "That helps", "That was helpful", "Very helpful", "Super helpful",
                "Thanks a bunch", "Much appreciated", "Thanks bot", "Thank you bot"
            ],
            "responses": [
                "You're welcome! Happy to help.",
                "My pleasure! Let me know if you need anything else.",
                "Glad I could assist you!"
            ]
        },
        {
            "tag": "admissions",
            "patterns": [
                "How do I apply for admission", "Admission process", "What are the admission requirements",
                "When does admission start", "How to get admitted", "Admission criteria",
                "Application deadline", "Apply for course", "Apply online", "Admission procedure",
                "Get admission", "Apply for admission", "Admission form", "Admission date",
                "Admission details", "Admission info", "How to apply", "Application process",
                "Can I get admission", "I want admission", "How to join", "Join university",
                "Admission eligibility", "Admission last date", "When admission open",
                "Admission notification", "New admission", "Fresh admission", "Admissions open"
            ],
            "responses": [
                "Admissions for the new academic year start in June. You can apply online through our university portal. Required documents include: 10th and 12th mark sheets, ID proof, and passport photos. The application fee is Rs. 500."
            ]
        },
        {
            "tag": "enrollment",
            "patterns": [
                "How to enroll", "Enrollment process", "When is enrollment", "Course enrollment",
                "Subject registration", "Semester enrollment", "Enrollment dates", "Register for courses",
                "Enrollment deadline", "Enroll in courses", "Enroll for semester", "Course registration",
                "Subject selection", "Enrollment how", "Enroll now", "Enrollment period",
                "When enrollment start", "Enrollment schedule", "Register subjects",
                "How to register", "Registration process", "Course selection"
            ],
            "responses": [
                "Enrollment for the current semester is open from the 1st to the 15th of each month. Visit the student portal to select your courses. Make sure all fee dues are cleared before enrollment."
            ]
        },
        {
            "tag": "fees",
            "patterns": [
                "What is the fee structure", "How much are the fees", "Fee payment", "Tuition fees",
                "Exam fees", "When is fee due", "How to pay fees", "Fee deadline", "Total fees",
                "Semester fees", "Fee details", "Fees information", "Fee amount", "Payment methods",
                "College fees", "University fees", "Annual fees", "Pay fees online", "Fee submission",
                "How much fee", "What are the fees", "Fees cost", "Fee charges", "Tuition cost",
                "Fee for course", "Fee for semester", "Fee structure details", "Payment options",
                "Fee info", "Tell me fee", "Fees details", "Cost of course", "Course fee"
            ],
            "responses": [
                "The fee structure varies by department. Generally, tuition fees range from Rs. 50,000 to Rs. 1,50,000 per semester. You can pay online through the student portal or via bank transfer. Fee payment deadline is usually 2 weeks before the semester starts."
            ]
        },
        {
            "tag": "exams",
            "patterns": [
                "When are exams", "Exam schedule", "Examination dates", "Final exam", "Midterm exam",
                "Exam results", "When do exams start", "Exam hall ticket", "Exam timetable",
                "Examination schedule", "Exam dates", "Upcoming exams", "Exam info",
                "Exam information", "Semester exam", "End sem exam", "Mid sem exam",
                "Internal exam", "External exam", "Exam pattern", "Exam syllabus",
                "When exam start", "Exam calendar", "Exam time table", "Date sheet",
                "Exam notification", "Exam form", "Exam registration", "Test dates"
            ],
            "responses": [
                "End-semester exams typically occur in November (Fall) and May (Spring). Mid-semester exams are in September and February. Check the academic calendar on the portal for exact dates."
            ]
        },
        {
            "tag": "attendance",
            "patterns": [
                "What is attendance rule", "Minimum attendance", "Attendance percentage",
                "Attendance requirement", "Can I miss classes", "Attendance policy",
                "How many classes can I skip", "Attendance limit", "Attendance criteria",
                "Attendance shortage", "Attendance rules", "My attendance", "Check attendance",
                "Attendance info", "Attendance guidelines", "Low attendance", "Attendance norms",
                "Required attendance", "Attendance percentage rule", "Attend classes",
                "Miss class", "Skip classes", "Bunk classes", "Attendance criteria for exam"
            ],
            "responses": [
                "Students must maintain a minimum of 75% attendance to be eligible for exams. Attendance is calculated per subject. Medical leave can be considered with proper documentation. Check your attendance in the student portal."
            ]
        },
        {
            "tag": "scholarships",
            "patterns": [
                "Available scholarships", "How to apply for scholarship", "Financial aid",
                "Merit scholarship", "Sports scholarship", "Scholarship criteria",
                "Merit cum means scholarship", "Government scholarships", "Scholarship info",
                "Scholarship details", "Apply scholarship", "Get scholarship", "Scholarship form",
                "Scholarship deadline", "Scholarship amount", "Types of scholarships",
                "Financial help", "Fee waiver", "Educational grant", "Student aid",
                "Scholarship programs", "Scholarship schemes", "Any scholarships",
                "What scholarships available", "Scholarship opportunities", "Financial assistance"
            ],
            "responses": [
                "We offer multiple scholarships: Merit Scholarship (for top 10% students), Sports Scholarship, SC/ST/OBC Scholarship, and Need-based Financial Aid. Applications open in July. Visit the scholarship portal for details."
            ]
        },
        {
            "tag": "hostel",
            "patterns": [
                "Hostel facilities", "Hostel admission", "Hostel fees", "Room allocation",
                "Hostel rules", "Boys hostel", "Girls hostel", "Accommodation", "Hostel application",
                "Hostel info", "Hostel details", "Apply for hostel", "Get hostel room",
                "Hostel availability", "Hostel charges", "Hostel cost", "Hostel room",
                "On campus stay", "Residential facility", "Dormitory", "Hostel registration",
                "Hostel facilities", "Hostel amenities", "Room in hostel", "Hostel booking",
                "Hostel allotment", "Campus accommodation", "Living on campus",
                "Accommodation on campus", "Stay in hostel", "Hostel information"
            ],
            "responses": [
                "We have separate hostels for boys and girls with 24/7 security. Hostel fees are Rs. 60,000 per year including mess charges. Apply for hostel through the student portal. Rooms are allocated on a first-come basis."
            ]
        },
        {
            "tag": "library",
            "patterns": [
                "Library timings", "Library books", "How to get library card", "Library facilities",
                "Digital library", "Book borrowing", "Library rules", "Late fee for books",
                "Library hours", "Library info", "Library details", "Library resources",
                "Online library", "E-library", "Study material", "Library card",
                "Borrow books", "Return books", "Library fine", "Library opening time",
                "Books available", "Library services", "Reading room", "Reference books",
                "Journals access", "Library membership", "Library usage", "Library timing"
            ],
            "responses": [
                "The central library is open from 8 AM to 10 PM on weekdays and 9 AM to 6 PM on weekends. You can borrow up to 5 books for 14 days. Overdue fine is Rs. 5 per day. Digital resources are available 24/7."
            ]
        },
        {
            "tag": "transport",
            "patterns": [
                "Bus routes", "Transport facilities", "College bus", "Bus fees", "Transport schedule",
                "Pickup points", "Bus timings", "College shuttle", "Transport info",
                "Bus service", "Transport details", "Bus timing", "Transport charges",
                "Transport cost", "Transport pass", "Bus pass", "Transportation",
                "College transport", "Bus facility", "Pickup and drop", "Bus route",
                "Transport route", "Vehicle facility", "Bus stops", "Transport fees",
                "College cab", "Shuttle service", "Bus information", "Transport office"
            ],
            "responses": [
                "We operate 25 buses covering major routes across the city. Annual transport fee is Rs. 25,000. Bus passes can be obtained from the transport office. Check the portal for route maps and timings."
            ]
        },
        {
            "tag": "contact",
            "patterns": [
                "Contact information", "Phone number", "Email address", "How to contact",
                "Office address", "Helpline", "Emergency contact", "Contact details",
                "Reach university", "University phone", "University email", "Office location",
                "Front office", "Enquiry number", "Toll free number", "Contact number",
                "Call university", "Email university", "University address", "Contact info"
            ],
            "responses": [
                "You can reach us at: Phone: 1800-123-4567 (Toll-free), Email: info@university.edu, Address: University Campus, Education Road, City. Our office is open Monday-Friday, 9 AM - 5 PM."
            ]
        },
        {
            "tag": "courses",
            "patterns": [
                "What courses are offered", "Degree programs", "Departments", "Available courses",
                "UG programs", "PG programs", "Engineering courses", "Management courses",
                "Course list", "Programs offered", "Courses available", "Study programs",
                "Undergraduate courses", "Postgraduate courses", "B.Tech", "M.Tech",
                "MBA", "BBA", "MCA", "BCA", "What to study", "Courses offered",
                "Academic programs", "Course details", "Degree courses", "Specializations"
            ],
            "responses": [
                "We offer B.Tech, BBA, BCA, MBA, MCA, and M.Tech programs across departments. Engineering specializations include CSE, ECE, Mechanical, Civil, and EEE. Check the admissions page for the full list."
            ]
        },
        {
            "tag": "faculty",
            "patterns": [
                "Faculty list", "Professors", "Department faculty", "Teacher information",
                "HOD contact", "Faculty details", "Teaching staff", "Lecturers",
                "Faculty members", "Staff directory", "Professor list", "Faculty info",
                "Teachers in college", "Department teachers", "Faculty contact",
                "Academic staff", "Department heads", "Dean info", "HOD details"
            ],
            "responses": [
                "Each department has qualified faculty with PhDs and industry experience. Visit the department page on our website for faculty profiles and contact information."
            ]
        },
        {
            "tag": "placements",
            "patterns": [
                "Placement statistics", "Campus recruitment", "Companies visiting",
                "Average package", "Placement cell", "Job opportunities", "Career services",
                "Placement rate", "Campus placements", "Job placements", "Placement records",
                "Companies recruiting", "Placement history", "Highest package",
                "Placement assistance", "Career guidance", "Job after graduation",
                "Campus hiring", "Placement info", "Training and placement",
                "Recruitment process", "Placement details", "Jobs on campus",
                "Employment opportunities", "Company placements"
            ],
            "responses": [
                "Our placement rate is 95% with top companies like Google, Microsoft, Amazon, TCS, and Infosys recruiting. Average package is Rs. 8 LPA. The placement cell conducts training sessions throughout the year."
            ]
        },
        {
            "tag": "events",
            "patterns": [
                "Upcoming events", "College events", "Cultural fest", "Tech fest",
                "Sports events", "Workshops", "Seminars", "Event calendar",
                "College festival", "Annual events", "Student activities",
                "Campus events", "Cultural programs", "Technical events",
                "Techfest", "Culturalfest", "Events and fests", "College programs",
                "Event schedule", "Events information", "Functions in college"
            ],
            "responses": [
                "We host an annual tech fest 'TechVista' in March, cultural fest 'Spectrum' in October, and sports meet in January. Check the events calendar on the portal for updates."
            ]
        },
        {
            "tag": "facilities",
            "patterns": [
                "What facilities are available", "Campus facilities", "College amenities",
                "Campus infrastructure", "Facilities on campus", "Facilities provided",
                "College facilities", "Available facilities", "Campus features",
                "Facilities in campus", "Amenities available", "College amenities",
                "Infrastructure details", "Campus features", "What facilities",
                "University facilities", "Campus offers", "What's on campus",
                "Things available on campus", "Campus services"
            ],
            "responses": [
                "Campus facilities include: Central Library, 24/7 WiFi, 3 cafeterias, sports complex (cricket, football, basketball, tennis), modern gym, medical center, ATM, post office, and student activity center."
            ]
        },
        {
            "tag": "identity",
            "patterns": [
                "Who are you", "What can you do", "Your name", "What are you",
                "Tell me about yourself", "Are you a bot", "What is your name",
                "Introduce yourself", "What is this", "Who is this", "About you",
                "Who am I talking to", "Are you human", "What do you do",
                "Your purpose", "Your role", "Hello robot", "Chatbot info"
            ],
            "responses": [
                "I'm the University Smart Assistant, an AI chatbot designed to help students with queries about admissions, fees, exams, and more. I'm available 24/7 to assist you!"
            ]
        },
        {
            "tag": "help",
            "patterns": [
                "Help me", "I need help", "What can you help with", "How do you work",
                "What do you know", "Help", "Help needed", "Need assistance",
                "What questions can you answer", "What do you help with",
                "Guide me", "Support needed", "I have a question", "Can you help",
                "Need information", "Looking for help", "Please help", "Assistance required"
            ],
            "responses": [
                "I can help you with: Admission queries, Fee information, Exam schedules, Enrollment details, Attendance rules, Scholarships, Hostel, Library, Transport, and general FAQs. Just ask your question!"
            ]
        },
        {
            "tag": "timetable",
            "patterns": [
                "Class timetable", "Schedule", "Class timing", "Daily schedule",
                "Weekly classes", "Time table", "Class routine", "Class schedule",
                "Lecture timings", "Class hours", "Timetable details", "Time table",
                "Class time table", "Weekly schedule", "Daily routine", "Class plan",
                "Schedule details", "When are classes", "Class timings"
            ],
            "responses": [
                "Class timetables are available on the student portal. Generally, classes run from 9 AM to 5 PM with a lunch break from 1-2 PM. Each class is 50 minutes."
            ]
        },
        {
            "tag": "grades",
            "patterns": [
                "How are grades calculated", "CGPA", "SGPA", "Grade system",
                "Marking scheme", "Result calculation", "Grade points", "GPA calculation",
                "Grading policy", "Marks distribution", "Internal marks",
                "External marks", "Evaluation pattern", "Result system",
                "Grade percentage", "SGPA calculation", "How to calculate CGPA"
            ],
            "responses": [
                "We follow a 10-point CGPA system. Semester GPA (SGPA) is calculated based on credits and grades. Final grade includes internal assessment (30%) and end-semester exam (70%)."
            ]
        },
        {
            "tag": "documents",
            "patterns": [
                "How to get documents", "Bonafide certificate", "Transfer certificate",
                "Migration certificate", "ID card", "Document request", "TC",
                "Character certificate", "Mark sheet", "Provisional certificate",
                "Degree certificate", "Documents required", "Apply for documents",
                "Get certificate", "Document verification", "Certificate request",
                "College documents", "Academic documents", "Get bonafide",
                "Certificate needed", "Need certificate", "Document application"
            ],
            "responses": [
                "You can request documents like bonafide, transfer certificate, and ID card through the student portal. Processing takes 3-5 working days. Visit the admin office for urgent requests."
            ]
        },
        {
            "tag": "grievance",
            "patterns": [
                "How to complaint", "Grievance cell", "File complaint", "Report issue",
                "Student grievance", "Feedback", "Complaint", "Lodge complaint",
                "Report problem", "Raise complaint", "Submit grievance",
                "Student complaint", "Feedback form", "Complaint procedure",
                "Report harassment", "Grievance redressal", "Issue reporting"
            ],
            "responses": [
                "You can submit grievances through the student portal or email grievance@university.edu. The grievance cell responds within 7 working days. For urgent issues, meet the Dean of Student Affairs."
            ]
        },
        {
            "tag": "cafeteria",
            "patterns": [
                "Cafeteria timings", "Food options", "Canteen", "Mess menu",
                "Food courts", "Cafeteria info", "Eating options", "Mess timings",
                "Canteen menu", "Food facility", "Dining hall", "Food on campus",
                "Where to eat", "Campus food", "Canteen hours", "Mess details",
                "Cafeteria menu", "Lunch options", "Breakfast timing",
                "Food availability", "Canteen info", "Mess info"
            ],
            "responses": [
                "We have 3 cafeterias and a main mess. Timings: Breakfast 7-9 AM, Lunch 12-2 PM, Snacks 4-6 PM, Dinner 7-9 PM. Both vegetarian and non-vegetarian options available."
            ]
        },
        {
            "tag": "sports",
            "patterns": [
                "Sports facilities", "Gym", "Sports complex", "Games available",
                "Sports equipment", "Sports info", "Gym timings", "Fitness center",
                "Athletic facilities", "Sports activities", "Outdoor games",
                "Indoor games", "Recreational facilities", "Sports ground",
                "Play ground", "Sports details", "Gym facility", "Sports options",
                "Games on campus", "Sports center", "Sports hall"
            ],
            "responses": [
                "We have facilities for cricket, football, basketball, tennis, badminton, table tennis, and a modern gym. The sports complex is open 6 AM-9 PM. Contact the sports coordinator for equipment."
            ]
        }
    ]
}

def get_wordnet_pos(treebank_tag):
    """Map POS tag to WordNet POS tag for better lemmatization"""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def tokenize(text):
    """Tokenize the input text with better handling"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove single character tokens and purely numeric tokens
    tokens = [t for t in tokens if len(t) > 1 or t.isalpha()]
    return tokens

def remove_stopwords(tokens):
    """Remove stopwords but keep question words"""
    filtered = []
    for token in tokens:
        if token not in custom_stopwords:
            filtered.append(token)
    return filtered

def apply_synonyms(tokens):
    """Apply synonyms to normalize words"""
    normalized = []
    for token in tokens:
        # Check if token has a synonym mapping
        token_lower = token.lower()
        if token_lower in SYNONYMS:
            normalized.append(SYNONYMS[token_lower])
        else:
            # Check partial matches
            found = False
            for key, value in SYNONYMS.items():
                if key in token_lower or token_lower in key:
                    normalized.append(value)
                    found = True
                    break
            if not found:
                normalized.append(token_lower)
    return normalized

def lemmatize(tokens):
    """Lemmatize the tokens with POS tagging for better accuracy"""
    try:
        # Get POS tags
        pos_tags = nltk.pos_tag(tokens)
        lemmatized = []
        for token, tag in pos_tags:
            wordnet_pos = get_wordnet_pos(tag)
            lemma = lemmatizer.lemmatize(token, pos=wordnet_pos)
            lemmatized.append(lemma.lower())
        return lemmatized
    except Exception as e:
        # Fallback to basic lemmatization
        return [lemmatizer.lemmatize(token).lower() for token in tokens]

def preprocess(text):
    """Complete preprocessing pipeline with all steps"""
    # Tokenize
    tokens = tokenize(text)
    # Remove stopwords
    tokens = remove_stopwords(tokens)
    # Apply synonyms
    tokens = apply_synonyms(tokens)
    # Lemmatize
    tokens = lemmatize(tokens)
    # Remove any remaining stopwords after lemmatization
    tokens = [t for t in tokens if t not in custom_stopwords and len(t) > 1]
    return tokens

def preprocess_for_tfidf(text):
    """Preprocess text for TF-IDF (returns string)"""
    tokens = preprocess(text)
    return ' '.join(tokens)

def create_training_data():
    """Create training data from intents"""
    words = []
    classes = []
    documents = []
    pattern_texts = []  # Store original patterns for TF-IDF

    for intent in INTENTS['intents']:
        for pattern in intent['patterns']:
            # Tokenize and lemmatize each pattern
            tokenized = preprocess(pattern)
            words.extend(tokenized)
            documents.append((tokenized, intent['tag']))
            pattern_texts.append((' '.join(tokenized), intent['tag']))

            # Add to classes if not already there
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # Remove duplicates and sort
    words = sorted(set([w for w in words if w.isalnum()]))
    classes = sorted(set(classes))

    return words, classes, documents, pattern_texts

def create_bow(tokenized_sentence, words):
    """Create bag of words vector"""
    bag = [0] * len(words)
    for word in tokenized_sentence:
        for i, w in enumerate(words):
            if w == word:
                bag[i] = 1
    return np.array(bag)

def save_training_data(words, classes, pattern_texts=None):
    """Save training data to files"""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)

    with open(os.path.join(model_dir, 'words.pkl'), 'wb') as f:
        pickle.dump(words, f)

    with open(os.path.join(model_dir, 'classes.pkl'), 'wb') as f:
        pickle.dump(classes, f)

    with open(os.path.join(model_dir, 'intents.json'), 'w') as f:
        json.dump(INTENTS, f, indent=2)

    # Save pattern texts for TF-IDF
    if pattern_texts:
        with open(os.path.join(model_dir, 'pattern_texts.pkl'), 'wb') as f:
            pickle.dump(pattern_texts, f)

def load_training_data():
    """Load training data from files"""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')

    words_path = os.path.join(model_dir, 'words.pkl')
    classes_path = os.path.join(model_dir, 'classes.pkl')
    pattern_texts_path = os.path.join(model_dir, 'pattern_texts.pkl')

    if not os.path.exists(words_path) or not os.path.exists(classes_path):
        words, classes, documents, pattern_texts = create_training_data()
        save_training_data(words, classes, pattern_texts)
        return words, classes, documents, pattern_texts

    with open(words_path, 'rb') as f:
        words = pickle.load(f)

    with open(classes_path, 'rb') as f:
        classes = pickle.load(f)

    pattern_texts = None
    if os.path.exists(pattern_texts_path):
        with open(pattern_texts_path, 'rb') as f:
            pattern_texts = pickle.load(f)

    return words, classes, None, pattern_texts

if __name__ == '__main__':
    words, classes, documents, pattern_texts = create_training_data()
    save_training_data(words, classes, pattern_texts)
    print(f"Created vocabulary with {len(words)} words and {len(classes)} intents")
    print(f"Classes: {classes}")
    print(f"Pattern texts: {len(pattern_texts)} patterns")
