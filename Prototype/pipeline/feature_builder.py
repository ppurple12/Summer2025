from models.agent_analyzer import AgentAnalyzer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.cluster import KMeans

def build_feature_matrix(people_data):
    analyzers = [AgentAnalyzer(p) for p in people_data]
    all_features = sorted(set(
        f for analyzer in analyzers for f in analyzer.features
    ))
    return analyzers, all_features

def preprocess_features(analyzers, max_features=200):
    corpus = [a.get_text() for a in analyzers]

    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(corpus)

    return X.toarray(), vectorizer

def cluster_people(X_scaled, n_clusters=3):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(X_scaled)
    return model, labels