"""
Spelling Error Correction Module
Automatically corrects common spelling mistakes in user queries before intent detection.
Uses dynamic vocabulary from project data (training data, FAQs) and common English words.
"""

import re
import os
import json
from difflib import get_close_matches

class SpellingCorrector:
    def __init__(self):
        # Common spelling corrections dictionary (highest priority)
        self.corrections = {
            # Scholarship related
            'scholship': 'scholarship',
            'scholarshp': 'scholarship',
            'scholership': 'scholarship',
            'scolarship': 'scholarship',
            
            # Library related
            'libary': 'library',
            'librery': 'library',
            'librari': 'library',
            'librarry': 'library',
            
            # Transport related
            'transprt': 'transport',
            'transprot': 'transport',
            'transpor': 'transport',
            
            # Hostel related
            'hostal': 'hostel',
            'hostle': 'hostel',
            'hostell': 'hostel',
            
            # Attendance related
            'attendence': 'attendance',
            'atendance': 'attendance',
            
            # Admissions related
            'admisions': 'admissions',
            'admision': 'admissions',
            
            # Exam related
            'exm': 'exam',
            
            # Common typos
            'whats': 'what',
            'wat': 'what',
            'wen': 'when',
            'were': 'where',
            'hw': 'how',
            'hows': 'how',
            'cant': 'cannot',
            'dnt': 'donot',
            'pls': 'please',
            'plz': 'please',
            'thnx': 'thanks',
            'thanx': 'thanks',
            'info': 'information',
            'detials': 'details',
            'detals': 'details',
        }
        
        # Build comprehensive vocabulary
        self.vocabulary = set()
        self._build_vocabulary()
    
    def _build_vocabulary(self):
        """Build vocabulary from multiple sources"""
        # 1. Add corrections dictionary values
        self.vocabulary.update(self.corrections.values())
        
        # 2. Load from training data (intents.json)
        self._load_from_training_data()
        
        # 3. Load common English words
        self._load_common_english_words()
        
        # 4. Add university-specific terms
        self._add_university_terms()
        
        print(f"[Spelling Corrector] Vocabulary built with {len(self.vocabulary)} words")
    
    def _load_from_training_data(self):
        """Load vocabulary from training intents.json"""
        try:
            intents_path = os.path.join(os.path.dirname(__file__), 'models', 'intents.json')
            if os.path.exists(intents_path):
                with open(intents_path, 'r', encoding='utf-8') as f:
                    intents_data = json.load(f)
                
                # Extract words from patterns
                for intent in intents_data.get('intents', []):
                    for pattern in intent.get('patterns', []):
                        words = re.findall(r'\b\w+\b', pattern.lower())
                        self.vocabulary.update(words)
                
                # Extract words from responses
                for intent in intents_data.get('intents', []):
                    response = intent.get('response', '')
                    words = re.findall(r'\b\w+\b', response.lower())
                    self.vocabulary.update(words)
                
                print(f"[Spelling Corrector] Loaded vocabulary from training data")
        except Exception as e:
            print(f"[Spelling Corrector] Error loading training data: {e}")
    
    def _load_common_english_words(self):
        """Load common English words"""
        common_words = [
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs',
            'this', 'that', 'these', 'those', 'who', 'whom', 'whose', 'which', 'what',
            
            # Common verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'ought',
            'go', 'goes', 'went', 'gone', 'come', 'comes', 'came', 'get', 'gets', 'got', 'gotten',
            'make', 'makes', 'made', 'know', 'knows', 'knew', 'known', 'think', 'thinks', 'thought',
            'take', 'takes', 'took', 'taken', 'see', 'sees', 'saw', 'seen', 'want', 'wants', 'wanted',
            'use', 'uses', 'used', 'find', 'finds', 'found', 'give', 'gives', 'gave', 'given',
            'tell', 'tells', 'told', 'ask', 'asks', 'asked', 'work', 'works', 'worked', 'seem',
            'seems', 'seemed', 'feel', 'feels', 'felt', 'try', 'tries', 'tried', 'leave', 'leaves', 'left',
            'call', 'calls', 'called', 'need', 'needs', 'needed', 'become', 'becomes', 'became', 'become',
            'put', 'puts', 'putting', 'mean', 'means', 'meant', 'keep', 'keeps', 'kept', 'let', 'lets',
            'begin', 'begins', 'began', 'begun', 'show', 'shows', 'showed', 'shown', 'hear', 'hears', 'heard',
            'play', 'plays', 'played', 'run', 'runs', 'ran', 'running', 'move', 'moves', 'moved',
            'live', 'lives', 'lived', 'believe', 'believes', 'believed', 'bring', 'brings', 'brought',
            'happen', 'happens', 'happened', 'write', 'writes', 'wrote', 'written', 'provide', 'provides',
            'provided', 'sit', 'sits', 'sat', 'stand', 'stands', 'stood', 'lose', 'loses', 'lost',
            'pay', 'pays', 'paid', 'meet', 'meets', 'met', 'include', 'includes', 'included',
            'continue', 'continues', 'continued', 'set', 'sets', 'setting', 'learn', 'learns', 'learned',
            'change', 'changes', 'changed', 'lead', 'leads', 'led', 'understand', 'understands', 'understood',
            'watch', 'watches', 'watched', 'follow', 'follows', 'followed', 'stop', 'stops', 'stopped',
            'create', 'creates', 'created', 'speak', 'speaks', 'spoke', 'spoken', 'read', 'reads', 'reading',
            'allow', 'allows', 'allowed', 'add', 'adds', 'added', 'spend', 'spends', 'spent', 'grow', 'grows',
            'grew', 'grown', 'open', 'opens', 'opened', 'walk', 'walks', 'walked', 'win', 'wins', 'won',
            'offer', 'offers', 'offered', 'remember', 'remembers', 'remembered', 'love', 'loves', 'loved',
            'consider', 'considers', 'considered', 'appear', 'appears', 'appeared', 'buy', 'buys', 'bought',
            'wait', 'waits', 'waited', 'serve', 'serves', 'served', 'die', 'dies', 'died', 'send', 'sends',
            'sent', 'expect', 'expects', 'expected', 'build', 'builds', 'built', 'stay', 'stays', 'stayed',
            'fall', 'falls', 'fell', 'fallen', 'cut', 'cuts', 'cutting', 'reach', 'reaches', 'reached',
            'kill', 'kills', 'killed', 'remain', 'remains', 'remained',
            
            # Common nouns
            'time', 'year', 'people', 'way', 'day', 'man', 'woman', 'child', 'thing', 'world',
            'life', 'part', 'school', 'student', 'system', 'program', 'question', 'work', 'government',
            'number', 'night', 'point', 'home', 'water', 'room', 'mother', 'area', 'money', 'story',
            'fact', 'month', 'lot', 'right', 'study', 'book', 'eye', 'job', 'word', 'business',
            'issue', 'side', 'kind', 'head', 'house', 'service', 'friend', 'father', 'power', 'hour',
            'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community', 'name', 'president',
            'team', 'minute', 'idea', 'kid', 'body', 'information', 'back', 'parent', 'face', 'others',
            'level', 'office', 'door', 'health', 'person', 'art', 'war', 'history', 'party', 'result',
            'change', 'morning', 'reason', 'research', 'girl', 'guy', 'food', 'moment', 'air', 'teacher',
            'force', 'education',
            
            # Adjectives
            'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
            'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
            'few', 'public', 'bad', 'same', 'able', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
            'by', 'from', 'up', 'about', 'into', 'over', 'after', 'beneath', 'under', 'above',
            'the', 'a', 'an', 'and', 'but', 'or', 'as', 'if', 'when', 'than', 'because', 'while',
            'where', 'after', 'so', 'though', 'since', 'until', 'whether', 'before', 'although', 'nor',
            
            # Numbers
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
            
            # Common connectors
            'also', 'there', 'use', 'any', 'make', 'like', 'him', 'into', 'time', 'has', 'look',
            'only', 'could', 'year', 'your', 'them', 'then', 'than', 'this', 'which', 'their', 'some',
            'would', 'each', 'about', 'will', 'other', 'more', 'when', 'out', 'through', 'we', 'think',
        ]
        
        self.vocabulary.update([w.lower() for w in common_words])
    
    def _add_university_terms(self):
        """Add university-specific terms to vocabulary"""
        university_terms = [
            'admission', 'admissions', 'scholarship', 'scholarships',
            'library', 'libraries', 'transport', 'transportation',
            'hostel', 'hostels', 'attendance', 'attendances',
            'exam', 'exams', 'examination', 'examinations',
            'fee', 'fees', 'department', 'departments',
            'timing', 'timings', 'schedule', 'schedules',
            'course', 'courses', 'semester', 'semesters',
            'faculty', 'staff', 'student', 'students',
            'computer', 'science', 'engineering', 'mechanical',
            'civil', 'electrical', 'electronics', 'information',
            'technology', 'management', 'business', 'arts',
            'commerce', 'science', 'education', 'university',
            'college', 'campus', 'building', 'room',
            'class', 'classes', 'lecture', 'lectures',
            'lab', 'laboratory', 'practical', 'theory',
            'mark', 'marks', 'grade', 'grades',
            'result', 'results', 'placement', 'job',
            'career', 'future', 'opportunity', 'opportunities',
            'help', 'support', 'assistance', 'guidance',
            'office', 'administration', 'admin', 'administration',
            'phone', 'email', 'address', 'contact',
            'website', 'portal', 'login', 'register',
            'password', 'username', 'account', 'profile',
            'form', 'application', 'document', 'certificate',
            'degree', 'diploma', 'certificate', 'certification',
            'program', 'programme', 'curriculum', 'syllabus',
            'book', 'books', 'journal', 'journals',
            'resource', 'resources', 'facility', 'facilities',
            'service', 'services', 'rule', 'rules',
            'regulation', 'regulations', 'policy', 'policies',
            'procedure', 'procedures', 'process', 'processes',
            'date', 'time', 'day', 'month', 'year',
            'morning', 'afternoon', 'evening', 'night',
            'week', 'month', 'semester', 'academic',
            'year', 'session', 'term', 'trimester',
            'cse', 'ece', 'me', 'ce', 'eee',
            'roll', 'number', 'enrollment', 'enroll',
            'register', 'registration', 'apply', 'application',
            'deadline', 'dates', 'duration', 'period',
            'amount', 'cost', 'price', 'payment',
            'structure', 'details', 'information', 'inquiry',
            'general', 'technical', 'support', 'feedback',
            'available', 'facility', 'amenities', 'wifi',
            'accommodation', 'booking', 'reservation', 'rules',
            'policy', 'percentage', 'required', 'minimum',
            'eligibility', 'criteria', 'requirements', 'documents',
            'upload', 'submit', 'process', 'status',
            'approved', 'rejected', 'pending', 'complete',
            'completed', 'ongoing', 'upcoming', 'past',
            'hall', 'ticket', 'announcement', 'notification',
            'digital', 'online', 'offline', 'portal',
            'dashboard', 'profile', 'settings', 'preferences',
        ]
        
        self.vocabulary.update([t.lower() for t in university_terms])
    
    def load_from_faq_data(self, faqs_col):
        """Load vocabulary from FAQ data in MongoDB"""
        try:
            if faqs_col is not None:
                faqs = list(faqs_col.find({}, {'question': 1, 'answer': 1}))
                for faq in faqs:
                    # Extract words from questions
                    question = faq.get('question', '')
                    words = re.findall(r'\b\w+\b', question.lower())
                    self.vocabulary.update(words)
                    
                    # Extract words from answers
                    answer = faq.get('answer', '')
                    words = re.findall(r'\b\w+\b', answer.lower())
                    self.vocabulary.update(words)
                
                print(f"[Spelling Corrector] Loaded vocabulary from {len(faqs)} FAQs")
        except Exception as e:
            print(f"[Spelling Corrector] Error loading FAQ data: {e}")
    
    def correct_word(self, word):
        """Correct a single word using dictionary and fuzzy matching"""
        word_lower = word.lower()
        
        # Direct dictionary lookup (highest priority)
        if word_lower in self.corrections:
            return self.corrections[word_lower]
        
        # If word is already in vocabulary, return as-is
        if word_lower in self.vocabulary:
            return word
        
        # Fuzzy matching for similar words
        # Only attempt fuzzy matching for words longer than 3 characters
        # Use a moderate threshold to catch typos without over-correcting
        if len(word) > 3:
            matches = get_close_matches(word_lower, self.vocabulary, n=1, cutoff=0.75)
            if matches:
                # Preserve original case if possible
                if word[0].isupper():
                    return matches[0].capitalize()
                return matches[0]
        
        return word
    
    def correct_query(self, query):
        """Correct spelling errors in the entire query"""
        if not query or not isinstance(query, str):
            return query
        
        # Split by whitespace to preserve punctuation attached to words
        tokens = query.split()
        
        corrected_tokens = []
        for token in tokens:
            # Separate word from trailing punctuation
            match = re.match(r'^(\w+)([^\w]*)$', token)
            if match:
                word = match.group(1)
                punctuation = match.group(2)
                
                # Correct the word if it's alphabetic
                if word.isalpha():
                    corrected_word = self.correct_word(word)
                    corrected_tokens.append(corrected_word + punctuation)
                else:
                    corrected_tokens.append(token)
            else:
                # Keep as-is if no word part
                corrected_tokens.append(token)
        
        # Reconstruct the query with spaces
        corrected_query = ' '.join(corrected_tokens)
        
        return corrected_query
    
    def get_corrections_made(self, original, corrected):
        """Return a list of corrections made for logging/debugging"""
        original_words = original.lower().split()
        corrected_words = corrected.lower().split()
        
        corrections = []
        for orig, corr in zip(original_words, corrected_words):
            if orig != corr:
                corrections.append((orig, corr))
        
        return corrections


# Singleton instance
_spelling_corrector = None

def get_spelling_corrector():
    """Get the singleton spelling corrector instance"""
    global _spelling_corrector
    if _spelling_corrector is None:
        _spelling_corrector = SpellingCorrector()
    return _spelling_corrector


def correct_spelling(query):
    """Convenience function to correct spelling in a query"""
    corrector = get_spelling_corrector()
    return corrector.correct_query(query)


if __name__ == '__main__':
    # Test the spelling corrector
    corrector = SpellingCorrector()
    
    test_cases = [
        'scholship information',
        'libary timings',
        'transprt facility',
        'hostal rules',
        'attendence policy',
        'admisions process',
        'exm schedule',
        'whats the fee structure',
        'libary book availability',
        'scholship for sc students',
        'hostal accomodation',
        'attendence percentage',
        'admisions deadline',
        'exm results',
        'computr science',
        'enginering',
        'departmet of cse',
        'universiti',
        'colleg',
    ]
    
    print("Spelling Correction Test Results:")
    print("=" * 60)
    for test in test_cases:
        corrected = corrector.correct_query(test)
        corrections = corrector.get_corrections_made(test, corrected)
        status = "OK" if test == corrected else "CORRECTED"
        print(f"\n{status}")
        print(f"Original:  {test}")
        print(f"Corrected: {corrected}")
        if corrections:
            print(f"Changes:   {corrections}")
