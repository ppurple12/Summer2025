from fastapi import APIRouter, HTTPException
import numpy as np
import faiss
from nltk.sentiment import SentimentIntensityAnalyzer
import onnxruntime
from transformers import AutoTokenizer

sentiment_analyzer = SentimentIntensityAnalyzer()
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
ort_session = onnxruntime.InferenceSession("all_mpnet_base_v2.onnx")

def onnx_embed(text):
    inputs = tokenizer(text, return_tensors="np", padding=True, truncation=True, max_length=512)
    
    # 🔧 Force inputs to int32 to match ONNX model expectations
    inputs["input_ids"] = inputs["input_ids"].astype("int32")
    inputs["attention_mask"] = inputs["attention_mask"].astype("int32")

    ort_inputs = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"]
    }

    ort_outs = ort_session.run(None, ort_inputs)
    return ort_outs[0][:, 0, :]

embedding_cache = {}

def get_embedding(text, embedder):
    if text not in embedding_cache:
        embedding_cache[text] = onnx_embed(text)[0]
    return embedding_cache[text]

def normalize_score(score, min_val=1, max_val=5):
    try:
        score = float(score)
        return 2 * ((score - min_val) / (max_val - min_val)) - 1  # scale to [-1, 1]
    except (ValueError, TypeError):
        return None
    
def analyze_documents(docs):
    semantic_texts = []
    sentiment_features = []
    import pprint
    pprint.pprint(docs)

    numeric_features = []

    for doc in docs: 
        # Reviews (text + sentiment)
        for review in doc.get("documents", {}).get("review", []):
            feedback = review.get("feedback", "")
            if feedback:
                semantic_texts.append(feedback)
                scores = sentiment_analyzer.polarity_scores(feedback)
                sentiment_features.append(np.array([
                    scores["neg"], scores["neu"], scores["pos"], scores["compound"]
                ]))

        # Surveys (mixed text and numeric)
        for survey in doc.get("documents", {}).get("survey", []):
            survey_sentiment = []
            for field, value in survey.items():
                if isinstance(value, (int, float)):
                    # Instead of raw numeric vector, create token for embedding
                    token = f"{field}_score_{str(value).replace('.', '_')}"
                    semantic_texts.append(token)

                    # Also collect for sentiment-like normalization if numeric
                    try:
                        score = float(value)
                        normalized_score = 2 * ((score - 1) / 4) - 1  # Assuming min=1 max=5, adjust if needed
                        survey_sentiment.append(normalized_score)
                    except Exception:
                        pass
                elif isinstance(value, str) and value.strip():
                    # Text survey fields also go into semantic texts
                    semantic_texts.append(value)

            if survey_sentiment:
                sentiment_features.append(np.array([
                    min(0.0, min(survey_sentiment)),
                    0.0,
                    max(0.0, max(survey_sentiment)),
                    np.mean(survey_sentiment)
                ]))

        # Other categories with free text
        for key in doc.get("documents", {}):
            if key in ["resume", "gamesheet", "other"]:
                for entry in doc.get("documents", {}).get(key, []):
                    if isinstance(entry, dict):
                        for field, text in entry.items():
                            if isinstance(text, str) and text.strip():
                                semantic_texts.append(text)
                                scores = sentiment_analyzer.polarity_scores(text)
                                sentiment_features.append(np.array([
                                    scores["neg"], scores["neu"], scores["pos"], scores["compound"]
                                ]))

        # If you have numeric stats in other places, similarly convert them to tokens and append to semantic_texts
        for stat_key in doc.get("documents", {}).get("statistics", {}):
            val = doc["documents"]["statistics"][stat_key]
            if isinstance(val, (int, float)):
                token = f"stat_{stat_key}_{str(val).replace('.', '_')}"
                semantic_texts.append(token)
            elif isinstance(val, str) and val.strip():
                semantic_texts.append(val)

    # Embedding: now includes numeric tokens as semantic texts
    if semantic_texts:
        combined_text = " ".join(semantic_texts)
        agent_embedding = get_embedding(combined_text)
    else:
        agent_embedding = np.zeros(768)

    # Sentiment vector aggregated as before
    if sentiment_features:
        sentiment_vector = np.mean(np.stack(sentiment_features), axis=0)
    else:
        sentiment_vector = np.zeros(4)

    # No separate numeric vector here - all numeric info encoded as tokens

    # Combine embedding + sentiment only
    combined_vector = np.concatenate([agent_embedding, sentiment_vector])

    return combined_vector


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
                text_to_role.append((text, role_name))
    dim = len(role_embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(role_embeddings).astype(np.float32))
    return index, text_to_role

