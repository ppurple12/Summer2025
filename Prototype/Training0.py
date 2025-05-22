from collections import defaultdict
import numpy as np
import json
import faiss

from models.agent_analyzer import AgentAnalyzer
import xgboost as xgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

from data.DataPreprocessing import preprocessed_data
from data.Traning_Labels import labels
from sentence_transformers import SentenceTransformer
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize the sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze_documents(docs, embedder):
    semantic_texts = []
    sentiment_features = []

   

    # 1. Reviews (typically contain natural language text)
    for review in docs.get("review", []):
        feedback = review.get("feedback", "")
        if feedback:
            semantic_texts.append(feedback)
            scores = sentiment_analyzer.polarity_scores(feedback)
            sentiment_features.append(np.array([
                scores["neg"], scores["neu"], scores["pos"], scores["compound"]
            ]))

    # 2. Survey (typically numerical scores)
    for survey in docs.get("survey", []):
        survey_sentiment = []
        for field in ["Engagement", "Happiness", "Motivation"]:
            if field in survey:
                # Normalize survey scores from [1–5] to [-1 to +1]
                normalized_score = 2 * ((survey[field] - 1) / 4) - 1
                survey_sentiment.append(normalized_score)
        if survey_sentiment:
            sentiment_features.append(np.array([
                min(0, min(survey_sentiment)),  # Negative
                0.0,                            # Neutral not applicable
                max(0, max(survey_sentiment)),  # Positive
                np.mean(survey_sentiment)       # Compound-like average
            ]))

    # 3. Resume (likely free-form text, no sentiment)
    resume = docs.get("resume", "")
    if isinstance(resume, str) and resume.strip():
        semantic_texts.append(resume)

    # 4. Gamesheet — only include if text/narrative is present
    gamesheet = docs.get("gamesheet", "")
    if isinstance(gamesheet, str) and gamesheet.strip():
        semantic_texts.append(gamesheet)
        scores = sentiment_analyzer.polarity_scores(gamesheet)
        sentiment_features.append(np.array([
            scores["neg"], scores["neu"], scores["pos"], scores["compound"]
        ]))

    # 5. Other — fallback category
    other = docs.get("other", "")
    if isinstance(other, str) and other.strip():
        semantic_texts.append(other)
        scores = sentiment_analyzer.polarity_scores(other)
        sentiment_features.append(np.array([
            scores["neg"], scores["neu"], scores["pos"], scores["compound"]
        ]))

    # Embed the combined semantic text
    if semantic_texts:
        combined_text = " ".join(semantic_texts)
        agent_embedding = get_embedding(combined_text, embedder)
    else:
        agent_embedding = np.zeros(embedder.get_sentence_embedding_dimension())

    # Combine all sentiment vectors
    if sentiment_features:
        sentiment_vector = np.mean(np.stack(sentiment_features), axis=0)
    else:
        sentiment_vector = np.zeros(4)

    # Final vector = semantic embedding + sentiment analysis
    return np.concatenate([agent_embedding, sentiment_vector])

# embedding cache to avoid recomputations - for roles
embedding_cache = {}
def get_embedding(text, embedder):
    if text not in embedding_cache:
        embedding_cache[text] = embedder.encode(text)
    return embedding_cache[text]

# precompute role embeddings with FAISS
def precompute_role_embeddings_with_faiss(roles_info, embedder):
    role_embeddings = []
    text_to_role = []
    seen_texts = {}

    for role_name, role_info in roles_info.items():
        keywords = [role_name] + role_info.get("positive", [])
        for text in keywords:
            if text not in seen_texts:
                vec = get_embedding(text, embedder)
                seen_texts[text] = vec
                role_embeddings.append(vec)
                text_to_role.append((text, role_name))  # for reverse lookup

    dim = len(role_embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(role_embeddings).astype(np.float32))

    return index, text_to_role

# load the embedding model
embedder = SentenceTransformer("all-mpnet-base-v2")

# load roles info
with open("roles.json", "r") as file:
    roles_info = json.load(file)

# precompute embeddings & FAISS index
faiss_index, text_to_role = precompute_role_embeddings_with_faiss(roles_info, embedder)

X_pairs = []
y_targets = []
agent_names_per_pair = []
trait_names_per_pair = []

top_k = 3  # number of closest role candidates to consider
added_pairs = set()
seen_agent_role_pairs = set()

# process each agent instance
for agent_data in preprocessed_data:
    agent_name = agent_data.get("agent_name")
    analyzer = AgentAnalyzer(agent_data)
    agent_text = analyzer.get_text()

    agent_vec = analyze_documents(agent_data.get("documents", {}), embedder)
    traits = labels.get(agent_name, {})

    for trait_name, score in traits.items():
        matched_role_name = None
        role_text = ""

        if trait_name in roles_info:
            matched_role_name = trait_name
            role_info = roles_info[matched_role_name]
            role_text = f"{role_info['prompt']} " + " ".join(role_info["positive"] + role_info["negative"])
        else:
            # FAISS match
            trait_vec = get_embedding(trait_name, embedder).astype(np.float32)
            trait_vec = trait_vec.reshape(1, -1)
            D, I = faiss_index.search(trait_vec, 1)
            top_idx = I[0][0]
            if top_idx != -1:
                candidate_text, matched_role = text_to_role[top_idx]
                if matched_role in roles_info:
                    matched_role_name = matched_role
                    role_info = roles_info[matched_role_name]
                    role_text = f"{role_info['prompt']} " + " ".join(role_info["positive"] + role_info["negative"])

        # if no match found - fallback to raw trait name
        if not role_text:
            matched_role_name = trait_name
            role_text = trait_name

        # prevent duplicates
        key = (agent_name, matched_role_name)
        if key in seen_agent_role_pairs:
            continue
        seen_agent_role_pairs.add(key)

        role_vec = get_embedding(role_text, embedder)

        role_vec = np.concatenate([role_vec, np.zeros(4)])
        combined_vec = np.concatenate([
            agent_vec,
            role_vec,
            np.abs(agent_vec - role_vec),
            agent_vec * role_vec
        ])

        X_pairs.append(combined_vec)
        y_targets.append(score)
        agent_names_per_pair.append(agent_name)
        trait_names_per_pair.append(matched_role_name)
            
# convert to numpy arrays
X = np.array(X_pairs)
y = np.array(y_targets)

# get train and test portions
X_train, X_test, y_train, y_test, agent_names_train, agent_names_test, trait_names_train, trait_names_test = train_test_split(
    X, y, agent_names_per_pair, trait_names_per_pair, test_size=0.2, random_state=42
)

# train XGBoost regressor
model = xgb.XGBRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# predict on test set
y_pred = model.predict(X_test)

# pair up agent and trait
agent_predictions = defaultdict(list)
for agent_name, trait_name, pred, actual in zip(agent_names_test, trait_names_test, y_pred, y_test):
    agent_predictions[agent_name].append((trait_name, pred, actual))

# display results n error
for agent, role_scores in agent_predictions.items():
    print(f"\nAgent: {agent}")
    for role, pred_score, actual_score in sorted(role_scores, key=lambda x: x[0]):
        print(f"  Role: {role:20s} Predicted: {pred_score:.2f}   Actual: {actual_score:.2f}")
        
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"\nMean Squared Error (MSE): {mse:.4f}")
print(f"Mean Absolute Error (MAE): {mae:.4f}")