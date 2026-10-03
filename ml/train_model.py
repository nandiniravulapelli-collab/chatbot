import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from ml.preprocessing import create_training_data, save_training_data, create_bow, preprocess_for_tfidf

def create_training_vectors(words, classes, documents):
    """Create training vectors"""
    train_x = []
    train_y = []

    for doc in documents:
        # doc is (tokenized_sentence, tag)
        bow = create_bow(doc[0], words)
        train_x.append(bow)

        # Create output row (one-hot encoding)
        output_row = [0] * len(classes)
        output_row[classes.index(doc[1])] = 1
        train_y.append(output_row)

    return np.array(train_x), np.array(train_y)

def build_model(input_size, output_size):
    """Build the ANN model with improved architecture"""
    model = Sequential()

    # Input layer with dropout
    model.add(Dense(256, input_shape=(input_size,), activation='relu'))
    model.add(Dropout(0.5))

    # Hidden layer 1
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.4))

    # Hidden layer 2
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))

    # Hidden layer 3
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))

    # Output layer with softmax
    model.add(Dense(output_size, activation='softmax'))

    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=0.005),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_tfidf(pattern_texts):
    """Train TF-IDF vectorizer on all patterns"""
    model_dir = os.path.join(os.path.dirname(__file__), 'models')

    # Extract patterns and tags
    all_patterns = []
    pattern_data = []

    for pattern, tag in pattern_texts:
        all_patterns.append(pattern)
        pattern_data.append({
            'pattern': pattern,
            'processed': pattern,
            'tag': tag
        })

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),  # Use unigrams and bigrams for better phrase matching
        max_features=2000,
        min_df=1,
        stop_words=None  # We already handle stopwords
    )

    tfidf_matrix = tfidf_vectorizer.fit_transform(all_patterns)

    # Save TF-IDF components
    with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'wb') as f:
        pickle.dump(tfidf_vectorizer, f)
    with open(os.path.join(model_dir, 'tfidf_matrix.pkl'), 'wb') as f:
        pickle.dump(tfidf_matrix, f)
    with open(os.path.join(model_dir, 'pattern_data.pkl'), 'wb') as f:
        pickle.dump(pattern_data, f)

    print(f"TF-IDF trained on {len(all_patterns)} patterns")
    print(f"TF-IDF vocabulary size: {len(tfidf_vectorizer.vocabulary_)}")

    return tfidf_vectorizer, tfidf_matrix, pattern_data

def train_model():
    """Train the intent classification model with TF-IDF support"""
    print("Creating training data...")
    result = create_training_data()

    # Handle both old and new return formats
    if len(result) == 4:
        words, classes, documents, pattern_texts = result
    else:
        words, classes, documents = result
        pattern_texts = []

    print(f"Vocabulary size: {len(words)}")
    print(f"Number of intents: {len(classes)}")
    print(f"Training samples: {len(documents)}")

    # Save vocabulary and classes
    save_training_data(words, classes, pattern_texts if pattern_texts else None)

    # Create training vectors
    print("Creating training vectors...")
    train_x, train_y = create_training_vectors(words, classes, documents)

    # Calculate class weights for imbalanced data
    from sklearn.utils.class_weight import compute_class_weight
    y_labels = np.argmax(train_y, axis=1)
    class_weights = compute_class_weight('balanced', classes=np.unique(y_labels), y=y_labels)
    class_weight_dict = dict(enumerate(class_weights))

    # Build model
    print("Building model...")
    model = build_model(len(words), len(classes))
    model.summary()

    # Train model
    print("Training model...")
    early_stopping = EarlyStopping(
        monitor='loss',
        patience=50,
        restore_best_weights=True
    )

    history = model.fit(
        train_x, train_y,
        epochs=300,
        batch_size=8,
        verbose=1,
        callbacks=[early_stopping],
        class_weight=class_weight_dict,
        validation_split=0.1
    )

    # Save model
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, 'chatbot_model.h5')
    model.save(model_path)

    print(f"\nModel saved to {model_path}")
    print(f"Final accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"Final loss: {history.history['loss'][-1]:.4f}")

    # Train TF-IDF if we have pattern texts
    if pattern_texts:
        print("\nTraining TF-IDF vectorizer...")
        train_tfidf(pattern_texts)

    return model, words, classes

def test_model(model, words, classes):
    """Test the model with sample inputs"""
    from preprocessing import preprocess

    test_sentences = [
        "Hello there",
        "What is the fee structure",
        "When are the exams",
        "I want to apply for hostel",
        "Thank you so much",
        "Facilities in campus",
        "What facilities are available on campus?",
        "Campus amenities",
        "Tell me about admissions",
        "Scholarship info"
    ]

    print("\nTesting model with sample inputs:")
    for sentence in test_sentences:
        tokens = preprocess(sentence)
        bow = create_bow(tokens, words)
        bow = bow.reshape(1, -1)

        prediction = model.predict(bow, verbose=0)[0]
        intent_index = np.argmax(prediction)
        confidence = prediction[intent_index]
        intent = classes[intent_index]

        print(f"Input: '{sentence}' -> Intent: '{intent}' (Confidence: {confidence:.4f})")

if __name__ == '__main__':
    model, words, classes = train_model()
    test_model(model, words, classes)
