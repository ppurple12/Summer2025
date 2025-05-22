from collections import defaultdict
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import scipy.sparse as sp
import json
import spacy
from sklearn.metrics import mean_squared_error, r2_score
from transformers import pipeline
from Training_Data import data
from Traning_Labels import labels
from pprint import pprint 

# Initialize spaCy for lemmatization (or any other preprocessing)
nlp = spacy.load("en_core_web_sm")

# Load pre-trained sentiment analyzer and topic model (Hugging Face transformers)
sentiment_analyzer = pipeline("sentiment-analysis")

# Function to extract role traits from text with embeddings
def extract_role_traits(text, role_keywords, embeddings_model=None):
    role_scores = defaultdict(int)
    lowered_text = text.lower()

    for role, terms in role_keywords.items():
        for word in terms["positive"]:
            if word.lower() in lowered_text:
                role_scores[role] += 1
        for word in terms["negative"]:
            if word.lower() in lowered_text:
                role_scores[role] -= 1
    
    # Integrating pre-trained embeddings or other NLP models
    if embeddings_model:
        # Example: calculating semantic similarity
        embeddings = embeddings_model.encode([text])
        # Further processing can happen here (e.g., using cosine similarity with role embeddings)
    
    return dict(role_scores)

# Modular text preprocessing
def preprocess_text(text):
    doc = nlp(text)
    # Lemmatization + remove stopwords
    return " ".join([token.lemma_ for token in doc if not token.is_stop])

# Function to load dynamic role definitions
def load_roles_from_json(role_file_path):
    with open(role_file_path, 'r') as f:
        return json.load(f)

# Process agent data - per agent 
grouped_text_data = defaultdict(str)
agent_identifiers = []  # stores both agent_id and agent_name 

for agent in data:
    a_id = agent.get("agent_id")
    identifier = a_id if a_id else agent.get("agent_name")

    # Skip if identifier or text is missing
    if not identifier or "text" not in agent:
        continue

    # If identifier is a list (e.g., multiple names or IDs), flatten
    identifiers = identifier if isinstance(identifier, list) else [identifier]

 
    for id in identifiers:
        if id not in grouped_text_data:
            agent_identifiers.append(id)
        for field, content in agent["text"].items():
            content_str = " ".join(f"{key}: {value}" for key, value in content.items()) if isinstance(content, dict) else str(content)
            grouped_text_data[id] += preprocess_text(content_str) + " "
# Filter and align labels based on identifiers (agent_id or agent_name)
labels_filtered = {identifier: labels[identifier] for identifier in agent_identifiers if identifier in labels}
labels_df_filtered = pd.DataFrame(labels_filtered).T.fillna(0)

# Extract role traits and build feature list
X = []
role_features = []

role_definitions = load_roles_from_json('roles.json')  # Load dynamic role definitions
pprint(grouped_text_data)
for agent_id in labels_filtered:
    # Get the roles the user has for this specific agent
    selected_roles = [role for role in labels[agent_id] if labels[agent_id][role] != 0]  # Only include non-zero roles
    
    # If no roles are selected, skip this agent (optional, based on data characteristics)
    if not selected_roles:
        continue
    
    # Get text data for this agent
    text_data = grouped_text_data[agent_id]
    
    # Extract role scores based on selected roles
    role_scores = extract_role_traits(
        text_data,
        {role: role_definitions[role] for role in selected_roles},
        embeddings_model=None  # Optionally pass a pre-trained embeddings model like 'Sentence-BERT' or 'GloVe'
    )
    
    # Append role features and text data
    role_features.append(role_scores)
    X.append(text_data)

# Convert to DataFrame for feature set
role_features_df = pd.DataFrame(role_features).fillna(0)

# Vectorize the text data (TF-IDF)
vectorizer = TfidfVectorizer(stop_words="english")
X_vectorized = vectorizer.fit_transform(X)

# Combine text features with role features
X_combined = sp.hstack([X_vectorized, sp.csr_matrix(role_features_df.values)])

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_combined, labels_df_filtered, test_size=0.16, random_state=42)

# Train the model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predict and evaluate
y_pred = rf_model.predict(X_test)

y_pred_selected = []

for i, pred in enumerate(y_pred):
    selected_roles = y_test.iloc[i].index[y_test.iloc[i] != 0].tolist()

    # Filter predictions to match the selected roles
    pred_selected = [pred[j] for j, role in enumerate(y_test.columns) if role in selected_roles]
    y_pred_selected.append(pred_selected)

for i in range(min(10, len(y_pred_selected))):
    test_row = y_test.iloc[i]
    selected_roles = test_row.index[test_row != 0].tolist()
    actual_selected = [round(float(val), 2) for val in test_row[selected_roles].values]
    predicted_values = [round(float(val), 2) for val in y_pred_selected[i]]
    print(f"Actual: {actual_selected}, Predicted: {predicted_values}")

# Evaluating the model using standard metrics
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}")
print(f"R-squared: {r2_score(y_test, y_pred)}")