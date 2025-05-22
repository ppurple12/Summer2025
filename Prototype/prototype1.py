'''
  Prototype1 - Testing SKLearn
  Testing the spaCy API for text processing
  Results:
  Meh. The results are less accurate
'''
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Load spaCy for text processing
nlp = spacy.load('en_core_web_sm')

# Initialize sentence transformer model for embedding
transformer_model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample data: Texts (documents) and their corresponding skill labels
data = [
    ("Led a team of engineers to develop a new software product", {"leadership": 0.9, "communication": 0.4, "problem solving": 0.6}),
    ("Conducted extensive market research to improve sales strategy", {"leadership": 0.0, "communication": 0.2, "problem solving": 0.5}),
    ("Resolved customer issues with software updates and patches", {"leadership": 0.2, "communication": 0.8, "problem solving": 0.85}),
    ("Did a great job fixing my printing issue! He was very quick and friendly during the interaction.", {"leadership": 0.4, "communication": 0.8, "problem solving": 0.4})
]

# Split text and labels
texts = [item[0] for item in data]
labels = [item[1] for item in data]

# Preprocess the text using spaCy (tokenization, lemmatization)
def preprocess_text(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

# Apply preprocessing to texts
texts = [preprocess_text(text) for text in texts]

# Prepare inputs and outputs
X = np.array([transformer_model.encode(text) for text in texts])  # Embedding representation of each document
y = np.array([[label["leadership"], label["communication"], label["problem solving"]] for label in labels])  # Skill scores

# Train/test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the model: Random Forest Regressor for multi-output regression
model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))

# Train the model
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)

# Calculate Mean Squared Error and R-squared for better evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Cross-validation for more robust performance estimation
cv_scores = cross_val_score(model, X, y, cv=3, scoring="neg_mean_squared_error")
print(f"Cross-validated Mean Squared Error: {-cv_scores.mean()}")

# Example: Predicting skill scores for a new document
new_text = "Farted a lot"
new_text = preprocess_text(new_text)
new_embedding = transformer_model.encode([new_text])
predicted_scores = model.predict(new_embedding)
print(f"Predicted skill scores: Leadership={predicted_scores[0][0]}, Communication={predicted_scores[0][1]}, Problem Solving={predicted_scores[0][2]}")