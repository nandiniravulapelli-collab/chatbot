# AI-Powered Smart University Assistant Chatbot

An intelligent chatbot system designed to help university students get instant answers to their queries about admissions, fees, exams, hostel, library, transport, and more.

## Features

- **AI Chatbot**: Natural language processing powered chatbot using NLTK and TensorFlow
- **Student Portal**: Registration, login, dashboard, and profile management
- **Admin Dashboard**: Manage FAQs, students, queries, fees, exams, and enrollment
- **Chat History**: View, search, and delete chat history
- **Responsive Design**: Dark/Light mode, mobile-friendly interface
- **Real-time Chat**: Typing animations, timestamps, and suggestion chips

## Technology Stack

### Frontend
- HTML5, CSS3, JavaScript (Vanilla)
- Bootstrap 5
- Animate.css

### Backend
- Python
- Flask (Web Framework)
- Flask REST API

### Database
- MongoDB (NoSQL Database)

### Machine Learning / NLP
- NLTK (Natural Language Toolkit)
- TensorFlow/Keras (Deep Learning)
- NumPy
- Scikit-learn

## Project Structure

```
project/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   └── js/
│       └── main.js        # Main JavaScript
│
├── templates/
│   ├── base.html          # Base template with navbar/footer
│   ├── index.html         # Home page
│   ├── about.html         # About page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Student dashboard
│   ├── admin.html         # Admin dashboard
│   ├── chat.html          # Chatbot interface
│   ├── profile.html       # User profile
│   ├── faq.html           # FAQ page
│   └── contact.html       # Contact page
│
├── ml/
│   ├── __init__.py
│   ├── preprocessing.py   # NLP preprocessing (tokenization, lemmatization)
│   ├── train_model.py     # Training script for ANN model
│   ├── predict.py         # Intent prediction module
│   └── models/            # Saved ML models
│
├── database/
│   ├── __init__.py
│   ├── connection.py      # Database connection
│   └── seed_data.py       # Database seed script
│
├── models/                # Data models
├── routes/                # API routes
└── controllers/           # Business logic
```

## NLP Pipeline

The chatbot processes user queries through the following stages:

1. **Tokenization**: Breaking text into individual tokens
2. **Lemmatization**: Converting words to their base form
3. **Bag of Words**: Creating feature vectors
4. **ANN Model**: Artificial Neural Network for classification
5. **Softmax Classifier**: Probability distribution over intents
6. **Intent Recognition**: Identifying user intent
7. **Knowledge Base Search**: Retrieving relevant information
8. **Response Generation**: Creating contextual responses

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB (installed and running)
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set up MongoDB

1. Install MongoDB Community Edition
2. Start MongoDB service:
   ```bash
   # Windows
   net start MongoDB

   # Linux/Mac
   sudo systemctl start mongod
   ```

### Initialize Database

```bash
python database/seed_data.py
```

### Train the ML Model (First Run)

```bash
cd ml
python train_model.py
```

This trains the neural network and saves the model to `ml/models/`.

### Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Default Credentials

After running the seed script, you can login with:

| Role    | Email                   | Password   |
|---------|-------------------------|------------|
| Admin   | admin@university.edu    | admin123   |
| Student | student@university.edu  | student123 |

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### User
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile

### Chatbot
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history/<id>` - Delete chat entry
- `DELETE /api/chat/history/clear` - Clear all history

### Admin
- `GET /api/admin/faqs` - List all FAQs
- `POST /api/admin/faqs` - Create FAQ
- `PUT /api/admin/faqs/<id>` - Update FAQ
- `DELETE /api/admin/faqs/<id>` - Delete FAQ
- `GET /api/admin/students` - List students
- `DELETE /api/admin/students/<id>` - Delete student
- `GET /api/admin/queries` - View student queries
- `GET /api/admin/analytics` - Dashboard analytics
- `POST /api/admin/fees` - Add fee structure
- `POST /api/admin/exams` - Add exam schedule
- `POST /api/admin/enrollment` - Add enrollment info

## User Modules

### Student Module
- **Registration**: Full name, roll number, department, email, password
- **Login**: Email and password authentication
- **Dashboard**: Quick actions, important dates, helpful tips
- **Chatbot**: Interactive AI assistant
- **Chat History**: View past conversations
- **Profile**: Update personal information

### Admin Module
- **Dashboard**: System analytics and statistics
- **Student Management**: View and manage registered students
- **FAQ Management**: Add, edit, delete frequently asked questions
- **Query Monitoring**: View all student queries
- **Fee Management**: Add fee structures per department
- **Exam Scheduling**: Add exam schedules
- **Enrollment Info**: Manage enrollment information

## Database Collections

| Collection | Description |
|------------|-------------|
| users | Student and admin accounts |
| faqs | Frequently asked questions |
| departments | Department information |
| fee_structure | Fee details per semester |
| enrollment_info | Enrollment periods and requirements |
| exam_schedule | Examination schedules |
| attendance_rules | Attendance policies |
| scholarships | Available scholarships |
| hostel | Hostel information |
| library | Library details |
| transport | Transport routes and fees |
| chat_history | User chat conversations |
| student_queries | Logged student queries |

## Features in Detail

### Chatbot Interface
- Real-time typing animation
- Message timestamps
- Suggestion chips for quick queries
- Chat history panel
- Dark/Light mode support
- Responsive design for mobile

### Intent Classification
The model recognizes 25+ intents including:
- Greetings, Goodbye, Thanks
- Admissions, Enrollment
- Fees, Exams, Attendance
- Scholarships, Hostel, Library, Transport
- Placements, Courses, Faculty
- Documents, Grievance
- Events, Cafeteria, Sports

### Security Features
- Password hashing with bcrypt
- Session management
- Role-based access control
- Input validation

## Configuration

Edit `config.py` to customize:

```python
SECRET_KEY = 'your-secret-key'
MONGO_URI = 'mongodb://localhost:27017/your_database'
```

## Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
mongod --version
sudo systemctl status mongod
```

### NLTK Data Download
If NLTK data is missing:
```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
```

### TensorFlow Installation
For systems with GPU:
```bash
pip install tensorflow[and-cuda]
```

## Screenshots

### Homepage
Professional university landing page with hero section, features, and statistics.

### Student Dashboard
Interactive dashboard with quick actions and important dates.

### Chatbot Interface
Modern chat interface with typing animations and suggestion chips.

### Admin Panel
Comprehensive admin dashboard with analytics and management features.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is developed as a minor project for educational purposes.

## Support

For any queries or issues:
- Email: info@university.edu
- Phone: 1800-123-4567
- Chatbot: Available 24/7

---

**Developed with Python, Flask, MongoDB, and TensorFlow**
