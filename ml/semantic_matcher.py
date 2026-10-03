import numpy as np
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from ml.preprocessing import preprocess_for_tfidf


class SemanticMatcher:
    """Enhanced semantic matching using improved TF-IDF and similarity analysis"""
    
    def __init__(self):
        """Initialize the enhanced semantic matcher"""
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.patterns = []
        self.intents = []
        self.model_dir = os.path.join(os.path.dirname(__file__), 'models')
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing semantic embeddings or initialize"""
        try:
            # Try to load existing semantic embeddings
            semantic_embeddings_path = os.path.join(self.model_dir, 'semantic_embeddings.pkl')
            semantic_patterns_path = os.path.join(self.model_dir, 'semantic_patterns.pkl')
            semantic_intents_path = os.path.join(self.model_dir, 'semantic_intents.pkl')
            
            if os.path.exists(semantic_embeddings_path) and os.path.exists(semantic_patterns_path):
                with open(semantic_embeddings_path, 'rb') as f:
                    self.tfidf_matrix = pickle.load(f)
                with open(semantic_patterns_path, 'rb') as f:
                    self.patterns = pickle.load(f)
                with open(semantic_intents_path, 'rb') as f:
                    self.intents = pickle.load(f)
                
                # Load vectorizer
                vectorizer_path = os.path.join(self.model_dir, 'semantic_vectorizer.pkl')
                if os.path.exists(vectorizer_path):
                    with open(vectorizer_path, 'rb') as f:
                        self.tfidf_vectorizer = pickle.load(f)
                
                print("Enhanced semantic matcher loaded from cache")
                return
        except Exception as e:
            print(f"Could not load semantic embeddings: {e}")
        
        # Initialize new
        self._build_semantic_embeddings()
    
    def _build_semantic_embeddings(self):
        """Build enhanced semantic embeddings using improved TF-IDF"""
        try:
            intents_path = os.path.join(self.model_dir, 'intents.json')
            if not os.path.exists(intents_path):
                print("intents.json not found")
                return
            
            # Load intents
            with open(intents_path, 'r') as f:
                intents_data = json.load(f)
            
            # Collect all patterns with their intents
            self.patterns = []
            self.intents = []
            
            for intent in intents_data['intents']:
                tag = intent['tag']
                for pattern in intent.get('patterns', []):
                    self.patterns.append(pattern)
                    self.intents.append(tag)
            
            # Create enhanced TF-IDF vectorizer with better parameters
            self.tfidf_vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),  # Use unigrams, bigrams, and trigrams
                max_features=3000,
                min_df=1,
                sublinear_tf=True,  # Use sublinear TF scaling
                analyzer='word',    # Word-level analysis
                stop_words='english' # Remove stop words
            )
            
            # Process patterns
            processed_patterns = [preprocess_for_tfidf(p) for p in self.patterns]
            
            # Generate TF-IDF matrix
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_patterns)
            
            # Save embeddings
            with open(os.path.join(self.model_dir, 'semantic_embeddings.pkl'), 'wb') as f:
                pickle.dump(self.tfidf_matrix, f)
            with open(os.path.join(self.model_dir, 'semantic_patterns.pkl'), 'wb') as f:
                pickle.dump(self.patterns, f)
            with open(os.path.join(self.model_dir, 'semantic_intents.pkl'), 'wb') as f:
                pickle.dump(self.intents, f)
            with open(os.path.join(self.model_dir, 'semantic_vectorizer.pkl'), 'wb') as f:
                pickle.dump(self.tfidf_vectorizer, f)
            
            print("Enhanced semantic embeddings built successfully")
            
        except Exception as e:
            print(f"Error building semantic embeddings: {e}")
            import traceback
            traceback.print_exc()
    
    def find_best_match(self, question, threshold=0.5, top_k=5):
        """
        Find the best semantic match for a question using enhanced similarity
        
        Args:
            question: User's question
            threshold: Minimum similarity threshold (0-1)
            top_k: Number of top matches to return
            
        Returns:
            tuple: (best_intent, best_confidence, matched_pattern, all_matches)
        """
        if self.tfidf_vectorizer is None or self.tfidf_matrix is None:
            return None, 0.0, None, []
        
        try:
            # Preprocess the question
            processed_question = preprocess_for_tfidf(question)
            
            # Transform the question using TF-IDF
            question_vector = self.tfidf_vectorizer.transform([processed_question])
            
            # Calculate cosine similarity with all patterns
            similarities = cosine_similarity(question_vector, self.tfidf_matrix).flatten()
            
            # Get top-k matches
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Prepare matches
            all_matches = []
            for idx in top_indices:
                confidence = float(similarities[idx])
                if confidence >= threshold:
                    all_matches.append({
                        'intent': self.intents[idx],
                        'confidence': confidence,
                        'pattern': self.patterns[idx]
                    })
            
            # Get the best match
            if all_matches:
                best_match = all_matches[0]
                return best_match['intent'], best_match['confidence'], best_match['pattern'], all_matches
            
            return None, 0.0, None, []
            
        except Exception as e:
            print(f"Error in semantic matching: {e}")
            return None, 0.0, None, []
    
    def rerank_candidates(self, question, candidates, weights=None):
        """
        Rerank candidates from different retrieval methods using enhanced similarity
        
        Args:
            question: User's question
            candidates: List of candidate dicts with 'intent', 'confidence', 'source'
            weights: Dict of weights for different sources
            
        Returns:
            List of reranked candidates
        """
        if self.tfidf_vectorizer is None or not candidates:
            return candidates
        
        if weights is None:
            weights = {'semantic': 0.4, 'tfidf': 0.3, 'ann': 0.3}
        
        try:
            # Preprocess question
            processed_question = preprocess_for_tfidf(question)
            question_vector = self.tfidf_vectorizer.transform([processed_question])
            
            # Calculate semantic scores for each candidate
            for candidate in candidates:
                if 'pattern' in candidate:
                    processed_pattern = preprocess_for_tfidf(candidate['pattern'])
                    pattern_vector = self.tfidf_vectorizer.transform([processed_pattern])
                    semantic_score = float(cosine_similarity(question_vector, pattern_vector)[0][0])
                    candidate['semantic_score'] = semantic_score
                else:
                    candidate['semantic_score'] = 0.0
            
            # Calculate combined scores
            for candidate in candidates:
                source = candidate.get('source', 'unknown')
                base_confidence = candidate.get('confidence', 0.0)
                semantic_score = candidate.get('semantic_score', 0.0)
                
                if source == 'semantic':
                    combined_score = (semantic_score * weights['semantic'] + 
                                    base_confidence * (1 - weights['semantic']))
                elif source == 'tfidf':
                    combined_score = (semantic_score * weights['semantic'] + 
                                    base_confidence * weights['tfidf'])
                elif source == 'ann':
                    combined_score = (semantic_score * weights['semantic'] + 
                                    base_confidence * weights['ann'])
                else:
                    combined_score = (semantic_score * 0.5 + base_confidence * 0.5)
                
                candidate['combined_score'] = combined_score
            
            # Sort by combined score
            reranked = sorted(candidates, key=lambda x: x['combined_score'], reverse=True)
            
            return reranked
            
        except Exception as e:
            print(f"Error in reranking: {e}")
            return candidates
    
    def is_available(self):
        """Check if the semantic matcher is available"""
        return self.tfidf_vectorizer is not None and self.tfidf_matrix is not None


# Global instance
semantic_matcher = None


def get_semantic_matcher():
    """Get or create the semantic matcher instance"""
    global semantic_matcher
    if semantic_matcher is None:
        semantic_matcher = SemanticMatcher()
    return semantic_matcher


def build_semantic_embeddings_if_needed():
    """Build semantic embeddings if they don't exist"""
    matcher = get_semantic_matcher()
    if not matcher.is_available():
        intents_path = os.path.join(os.path.dirname(__file__), 'models', 'intents.json')
        if os.path.exists(intents_path):
            print("Building enhanced semantic embeddings...")
            matcher._build_semantic_embeddings()
        else:
            print("intents.json not found, cannot build semantic embeddings")
    return matcher


if __name__ == '__main__':
    # Test the semantic matcher
    print("Testing Enhanced Semantic Matcher...")
    
    matcher = get_semantic_matcher()
    
    if matcher.is_available():
        # Test with semantically similar questions
        test_questions = [
            "What are the timings of the library?",
            "At which time does the library open?",
            "When is the library open?",
            "Library hours",
            "What time does library close?"
        ]
        
        print("\nTesting semantic similarity:")
        for q in test_questions:
            intent, confidence, pattern, matches = matcher.find_best_match(q, threshold=0.4)
            print(f"\nQuestion: {q}")
            print(f"Best Match: {intent} (confidence: {confidence:.3f})")
            print(f"Matched Pattern: {pattern}")
            if matches:
                print(f"Top {len(matches)} matches:")
                for i, match in enumerate(matches[:3], 1):
                    print(f"  {i}. {match['intent']} ({match['confidence']:.3f}): {match['pattern']}")
    else:
        print("Enhanced semantic matcher not available")
