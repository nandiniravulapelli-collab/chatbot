import numpy as np
import os
import pickle
import json
from ml.preprocessing import preprocess, preprocess_for_tfidf, create_training_data
from datetime import datetime
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ml.semantic_matcher import get_semantic_matcher, build_semantic_embeddings_if_needed
from ml.spelling_corrector import correct_spelling, get_spelling_corrector

# Load model and training data
model = None
words = None
classes = None
intents = None
tfidf_vectorizer = None
tfidf_matrix = None
pattern_data = None

def load_model_and_data():
    """Load the trained model and vocabulary"""
    global model, words, classes, intents, tfidf_vectorizer, tfidf_matrix, pattern_data

    model_dir = os.path.join(os.path.dirname(__file__), 'models')

    try:
        from tensorflow.keras.models import load_model
        model_path = os.path.join(model_dir, 'chatbot_model.h5')

        if not os.path.exists(model_path):
            print("Model not found. Training new model...")
            from ml.train_model import train_model
            model, words, classes = train_model()
        else:
            model = load_model(model_path)

        words_path = os.path.join(model_dir, 'words.pkl')
        classes_path = os.path.join(model_dir, 'classes.pkl')
        intents_path = os.path.join(model_dir, 'intents.json')
        tfidf_path = os.path.join(model_dir, 'tfidf_vectorizer.pkl')
        tfidf_matrix_path = os.path.join(model_dir, 'tfidf_matrix.pkl')
        pattern_data_path = os.path.join(model_dir, 'pattern_data.pkl')

        if os.path.exists(words_path):
            with open(words_path, 'rb') as f:
                words = pickle.load(f)

        if os.path.exists(classes_path):
            with open(classes_path, 'rb') as f:
                classes = pickle.load(f)

        if os.path.exists(intents_path):
            with open(intents_path, 'r') as f:
                intents = json.load(f)

        # Load or create TF-IDF vectorizer
        if os.path.exists(tfidf_path) and os.path.exists(tfidf_matrix_path) and os.path.exists(pattern_data_path):
            with open(tfidf_path, 'rb') as f:
                tfidf_vectorizer = pickle.load(f)
            with open(tfidf_matrix_path, 'rb') as f:
                tfidf_matrix = pickle.load(f)
            with open(pattern_data_path, 'rb') as f:
                pattern_data = pickle.load(f)
        else:
            # Create TF-IDF vectorizer from training data
            init_tfidf_vectorizer()

        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False

def init_tfidf_vectorizer():
    """Initialize TF-IDF vectorizer with training patterns"""
    global tfidf_vectorizer, tfidf_matrix, pattern_data

    if intents is None:
        return

    # Collect all patterns with their tags
    all_patterns = []
    pattern_data = []  # List of (pattern, tag, response)

    for intent in intents['intents']:
        tag = intent['tag']
        responses = intent.get('responses', [])
        for pattern in intent.get('patterns', []):
            processed = preprocess_for_tfidf(pattern)
            all_patterns.append(processed)
            pattern_data.append({
                'pattern': pattern,
                'processed': processed,
                'tag': tag,
                'response': responses[0] if responses else None
            })

    if all_patterns:
        # Create and fit TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=2000,
            min_df=1
        )
        tfidf_matrix = tfidf_vectorizer.fit_transform(all_patterns)

        # Save to files
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'wb') as f:
            pickle.dump(tfidf_vectorizer, f)
        with open(os.path.join(model_dir, 'tfidf_matrix.pkl'), 'wb') as f:
            pickle.dump(tfidf_matrix, f)
        with open(os.path.join(model_dir, 'pattern_data.pkl'), 'wb') as f:
            pickle.dump(pattern_data, f)

def tfidf_similarity_search(question, threshold=0.4):
    """Search for similar questions using TF-IDF and cosine similarity
    
    Returns:
        tuple: (intent_tag, confidence, response, context_dict, source)
    """
    global tfidf_vectorizer, tfidf_matrix, pattern_data

    if tfidf_vectorizer is None or tfidf_matrix is None or pattern_data is None:
        return None, 0.0, None, {}, 'tfidf'

    try:
        # Preprocess the question
        processed_question = preprocess_for_tfidf(question)

        # Transform the question using TF-IDF
        question_vector = tfidf_vectorizer.transform([processed_question])

        # Calculate cosine similarity with all patterns
        similarities = cosine_similarity(question_vector, tfidf_matrix).flatten()

        # Get the best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]

        if best_similarity >= threshold:
            match = pattern_data[best_idx]
            context = {
                'intent': match['tag'],
                'matched_pattern': match['pattern'],
                'similarity_score': float(best_similarity),
                'source': 'tfidf'
            }
            response = match.get('response', None)
            return match['tag'], best_similarity, response, context, 'tfidf'

        return None, best_similarity, None, {}, 'tfidf'
    except Exception as e:
        print(f"TF-IDF similarity error: {e}")
        return None, 0.0, None, {}, 'tfidf'

def get_response_from_intent(intent_tag):
    """Get a random response for the given intent"""
    global intents

    if intents is None:
        return "I'm here to assist you with your university queries. Could you please rephrase your question?"

    for intent in intents['intents']:
        if intent['tag'] == intent_tag:
            return random.choice(intent['responses'])

    return "I couldn't understand your query. Please try rephrasing or contact the admin office for assistance."

def search_knowledge_base(intent, question, faqs_col, departments_col, fee_structure_col,
                          enrollment_col, exam_schedule_col, attendance_col,
                          scholarships_col, hostel_col, library_col, transport_col):
    """Search knowledge base for more specific information using improved matching
    
    Returns:
        tuple: (response_string, context_dict) where context_dict contains the raw data
    """
    question_lower = question.lower()
    question_tokens = set(preprocess(question))
    context = {}

    # Check FAQs with improved matching
    if faqs_col is not None:
        # First try exact regex match
        faq = faqs_col.find_one({
            'question': {'$regex': question_lower, '$options': 'i'}
        })

        if not faq:
            # Try keyword matching
            all_faqs = list(faqs_col.find({}))
            best_faq = None
            best_score = 0

            for f in all_faqs:
                faq_tokens = set(preprocess(f.get('question', '')))
                # Calculate Jaccard similarity
                intersection = len(question_tokens & faq_tokens)
                union = len(question_tokens | faq_tokens)
                if union > 0:
                    score = intersection / union
                    if score > best_score and score > 0.3:
                        best_score = score
                        best_faq = f

            if best_faq:
                faq = best_faq

        if faq:
            context['faq'] = {
                'question': faq.get('question'),
                'answer': faq.get('answer'),
                'category': faq.get('category', 'general')
            }
            return faq['answer'], context

    # Check fee structure
    if intent in ['fees', 'fee'] and fee_structure_col is not None:
        try:
            fee = list(fee_structure_col.find().limit(1))
            if fee:
                f = fee[0]
                context['fee_structure'] = {
                    'tuition_fee': f.get('tuition_fee', 'N/A'),
                    'exam_fee': f.get('exam_fee', 'N/A'),
                    'library_fee': f.get('library_fee', 'N/A'),
                    'lab_fee': f.get('lab_fee', 'N/A'),
                    'total': f.get('total', 'N/A')
                }
                response = f"Tuition Fee: Rs. {f.get('tuition_fee', 'N/A')}, Exam Fee: Rs. {f.get('exam_fee', 'N/A')}, Library Fee: Rs. {f.get('library_fee', 'N/A')}. Total: Rs. {f.get('total', 'N/A')} per semester."
                return response, context
        except:
            pass

    # Check exam schedule
    if intent in ['exams', 'exam'] and exam_schedule_col is not None:
        try:
            exams = list(exam_schedule_col.find().limit(3))
            if exams:
                context['exam_schedule'] = []
                response = "Upcoming Exams:\n"
                for exam in exams:
                    context['exam_schedule'].append({
                        'exam_name': exam.get('exam_name', 'N/A'),
                        'start_date': exam.get('start_date', 'N/A'),
                        'end_date': exam.get('end_date', 'N/A'),
                        'description': exam.get('description', '')
                    })
                    response += f"- {exam.get('exam_name', 'N/A')}: {exam.get('start_date', 'N/A')} to {exam.get('end_date', 'N/A')}\n"
                return response, context
        except:
            pass

    # Check scholarships
    if intent in ['scholarships', 'scholarship'] and scholarships_col is not None:
        try:
            scholarships = list(scholarships_col.find().limit(5))
            if scholarships:
                context['scholarships'] = []
                response = "Available Scholarships:\n"
                for s in scholarships:
                    context['scholarships'].append({
                        'name': s.get('name', 'Scholarship'),
                        'description': s.get('description', ''),
                        'eligibility': s.get('eligibility', '')
                    })
                    response += f"- {s.get('name', 'Scholarship')}: {s.get('description', '')}\n"
                return response, context
        except:
            pass

    # Check hostel
    if intent in ['hostel', 'hostels', 'accommodation'] and hostel_col is not None:
        try:
            hostel = list(hostel_col.find().limit(1))
            if hostel:
                h = hostel[0]
                context['hostel'] = {
                    'fee': h.get('fee', 'N/A'),
                    'room_type': h.get('room_type', 'Single/Double Occupancy'),
                    'amenities': h.get('amenities', 'WiFi, Laundry, Common Room')
                }
                response = f"Hostel Fee: Rs. {h.get('fee', 'N/A')}/year. Rooms: {h.get('room_type', 'Single/Double Occupancy')}. Amenities: {h.get('amenities', 'WiFi, Laundry, Common Room')}."
                return response, context
        except:
            pass

    # Check library
    if intent in ['library', 'libraries'] and library_col is not None:
        try:
            library = list(library_col.find().limit(1))
            if library:
                lib = library[0]
                context['library'] = {
                    'timings': lib.get('timings', '8 AM - 10 PM'),
                    'max_books': lib.get('max_books', '5'),
                    'fine_per_day': lib.get('fine_per_day', '5')
                }
                response = f"Library Timings: {lib.get('timings', '8 AM - 10 PM')}. Max Books: {lib.get('max_books', '5')}. Fine: Rs. {lib.get('fine_per_day', '5')}/day."
                return response, context
        except:
            pass

    # Check transport
    if intent in ['transport', 'transportation', 'bus'] and transport_col is not None:
        try:
            transport = list(transport_col.find().limit(1))
            if transport:
                t = transport[0]
                routes = t.get('routes', [])
                if isinstance(routes, list):
                    route_count = len(routes)
                else:
                    route_count = t.get('total_buses', 25)
                context['transport'] = {
                    'annual_fee': t.get('annual_fee', 25000),
                    'route_count': route_count,
                    'timings': '6 AM - 8 PM'
                }
                response = f"Transport Fee: Rs. {t.get('annual_fee', 25000)}/year. Routes: {route_count}. Timings: 6 AM - 8 PM."
                return response, context
        except:
            pass

    # Check enrollment
    if intent in ['enrollment', 'register'] and enrollment_col is not None:
        try:
            enrollment = list(enrollment_col.find().limit(1))
            if enrollment:
                e = enrollment[0]
                context['enrollment'] = {
                    'start_date': e.get('start_date', 'N/A'),
                    'end_date': e.get('end_date', 'N/A'),
                    'requirements': e.get('requirements', 'Clear all dues, Course selection')
                }
                response = f"Enrollment Period: {e.get('start_date', 'N/A')} to {e.get('end_date', 'N/A')}. Requirements: {e.get('requirements', 'Clear all dues, Course selection')}."
                return response, context
        except:
            pass

    return None, context

def predict_intent(question, faqs_col=None, departments_col=None, fee_structure_col=None,
                   enrollment_col=None, exam_schedule_col=None, attendance_col=None,
                   scholarships_col=None, hostel_col=None, library_col=None, transport_col=None,
                   return_context=False):
    """Predict intent and generate response using semantic matching + TF-IDF + ANN with reranking
    
    Args:
        question: User's question
        faqs_col: MongoDB FAQs collection
        departments_col: MongoDB departments collection
        fee_structure_col: MongoDB fee structure collection
        enrollment_col: MongoDB enrollment collection
        exam_schedule_col: MongoDB exam schedule collection
        attendance_col: MongoDB attendance collection
        scholarships_col: MongoDB scholarships collection
        hostel_col: MongoDB hostel collection
        library_col: MongoDB library collection
        transport_col: MongoDB transport collection
        return_context: If True, return context dict along with response
    
    Returns:
        If return_context=True: (intent, confidence, response, context_dict)
        If return_context=False: (intent, confidence, response)
    """

    # STEP 0: Apply spelling correction to the query
    original_question = question
    corrected_question = correct_spelling(question)
    
    # Load FAQ vocabulary if available
    corrector = get_spelling_corrector()
    if faqs_col is not None:
        corrector.load_from_faq_data(faqs_col)
    
    # Log if correction was made
    if original_question != corrected_question:
        print(f"[Spelling Correction] '{original_question}' -> '{corrected_question}'")
    
    # Use corrected question for all processing
    question = corrected_question

    # Load model if not loaded
    global model, words, classes, tfidf_vectorizer, tfidf_matrix
    if model is None:
        load_model_and_data()

    # Initialize semantic matcher
    semantic_matcher = build_semantic_embeddings_if_needed()

    if model is None or words is None or classes is None:
        # Fallback response if model not available
        context = {} if return_context else None
        fallback_response = "I'm having trouble processing your request. Please try again or contact the helpdesk at 1800-123-4567."
        if return_context:
            return "unknown", 0.0, fallback_response, context
        return "unknown", 0.0, fallback_response

    try:
        # Initialize context dict
        context = {} if return_context else None

        # STEP 1: Collect candidates from multiple sources
        candidates = []

        # A. Semantic matching (if available)
        if semantic_matcher and semantic_matcher.is_available():
            semantic_intent, semantic_confidence, semantic_pattern, semantic_matches = \
                semantic_matcher.find_best_match(question, threshold=0.55, top_k=3)
            if semantic_intent and semantic_confidence >= 0.55:
                candidates.append({
                    'intent': semantic_intent,
                    'confidence': semantic_confidence,
                    'pattern': semantic_pattern,
                    'source': 'semantic',
                    'response': get_response_from_intent(semantic_intent)
                })

        # B. TF-IDF similarity search
        tfidf_intent, tfidf_confidence, tfidf_response, tfidf_context, tfidf_source = \
            tfidf_similarity_search(question, threshold=0.4)
        if tfidf_intent and tfidf_confidence >= 0.4:
            candidates.append({
                'intent': tfidf_intent,
                'confidence': tfidf_confidence,
                'pattern': tfidf_context.get('matched_pattern', ''),
                'source': 'tfidf',
                'response': tfidf_response or get_response_from_intent(tfidf_intent)
            })
            if return_context and tfidf_context:
                context.update(tfidf_context)

        # C. ANN model prediction
        tokens = preprocess(question)
        if len(tokens) > 0:
            bow = np.zeros(len(words))
            for word in tokens:
                if word in words:
                    idx = words.index(word)
                    bow[idx] = 1
            bow = bow.reshape(1, -1)
            prediction = model.predict(bow, verbose=0)[0]
            intent_index = np.argmax(prediction)
            ann_confidence = float(prediction[intent_index])
            ann_intent = classes[intent_index]
            
            if ann_confidence >= 0.3:
                candidates.append({
                    'intent': ann_intent,
                    'confidence': ann_confidence,
                    'pattern': '',
                    'source': 'ann',
                    'response': get_response_from_intent(ann_intent)
                })

        # STEP 2: Rerank candidates using semantic similarity
        if candidates and semantic_matcher and semantic_matcher.is_available():
            candidates = semantic_matcher.rerank_candidates(question, candidates)

        # STEP 3: Select best candidate
        if candidates:
            best_candidate = candidates[0]
            best_intent = best_candidate['intent']
            best_confidence = best_candidate['confidence']
            best_response = best_candidate['response']
            best_source = best_candidate['source']

            # Apply confidence thresholds based on source
            if best_source == 'semantic' and best_confidence >= 0.55:
                # High confidence semantic match
                pass  # Accept as is
            elif best_source == 'tfidf' and best_confidence >= 0.45:
                # High confidence TF-IDF match
                pass  # Accept as is
            elif best_source == 'ann' and best_confidence >= 0.5:
                # High confidence ANN match
                pass  # Accept as is
            elif best_confidence >= 0.4:
                # Medium confidence - accept but with warning
                pass  # Accept
            else:
                # Low confidence - fallback
                best_intent = "unknown"
                best_confidence = best_confidence
                best_response = get_fallback_response()
                best_source = 'fallback'

            # STEP 4: Knowledge base search for additional context
            kb_response, kb_context = search_knowledge_base(
                best_intent, question, faqs_col, departments_col, fee_structure_col,
                enrollment_col, exam_schedule_col, attendance_col,
                scholarships_col, hostel_col, library_col, transport_col
            )
            if return_context and kb_context:
                context.update(kb_context)
            
            # Add source to context
            if return_context:
                context['response_source'] = best_source
                context['confidence_source'] = best_source
                context['all_candidates'] = candidates[:3]  # Top 3 candidates for debugging

            # Use KB response if available, otherwise use candidate response
            final_response = kb_response if kb_response else best_response

            if return_context:
                return best_intent, best_confidence, final_response, context
            return best_intent, best_confidence, final_response

        # STEP 5: Fallback if no candidates
        fallback_response = get_fallback_response()
        if return_context:
            context['response_source'] = 'fallback'
            context['confidence_source'] = 'fallback'
            return "unknown", 0.0, fallback_response, context
        return "unknown", 0.0, fallback_response

    except Exception as e:
        print(f"Error predicting intent: {e}")
        import traceback
        traceback.print_exc()
        error_response = "I encountered an error processing your question. Please try again or contact the helpdesk."
        if return_context:
            return "error", 0.0, error_response, {}
        return "error", 0.0, error_response


def get_fallback_response():
    """Get a helpful fallback response when confidence is low"""
    fallback_responses = [
        "I'm not sure I fully understood your question. Could you please rephrase it? You can ask about admissions, fees, exams, hostel, library, transport, or scholarships.",
        "I didn't quite catch that. Try asking about: admission process, fee details, exam schedules, hostel facilities, library timings, or transport routes.",
        "Could you be more specific? I can help with university-related queries like admissions, fees, exams, attendance, scholarships, hostel, library, and transport."
    ]
    return random.choice(fallback_responses)

# Initialize model on import
try:
    load_model_and_data()
except Exception as e:
    print(f"Initialization error: {e}")

if __name__ == '__main__':
    # Test the predictor
    test_questions = [
        "Hello, how are you?",
        "What is the fee for CSE?",
        "When do exams start?",
        "I want to apply for hostel",
        "Tell me about scholarships",
        "What are the library timings?",
        "How can I get admission?",
        "Facilities in campus",
        "What facilities are available on campus?",
        "Campus facilities",
        "Amenities available",
        "Fee structure",
        "How much are the fees",
        "Hostel info",
        "Bus routes",
        "Sports",
        "Gym timing"
    ]

    print("\nTesting Intent Prediction:\n")
    for q in test_questions:
        intent, conf, response, context = predict_intent(q, return_context=True)
        print(f"Q: {q}")
        print(f"Intent: {intent} (Confidence: {conf:.4f})")
        print(f"Response: {response[:100]}..." if len(response) > 100 else f"Response: {response}")
        if context:
            print(f"Context: {context}")
        print()
