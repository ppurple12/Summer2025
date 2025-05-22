'''
  Prototype0 - Testing Scentence Transformer
  Testing the sentence_transformers API to compare with others.
  Results:
  Okay. Will need post processing like normalization and more training.
'''
from sentence_transformers import SentenceTransformer, util
import pandas as pd

# Sample agent descriptions (e.g. from resumes, surveys)
agent_texts = {
    "Agent 1": "Strong communication and leadership. Worked as manager with numerous employees under supervision. Managed technical teams and solved customer issues.",
    "Agent 2": "Experienced in data analysis and machine learning. Great attention to detail.",
    "Agent 3": "Worked in customer support. Problem-solver with good multitasking abilities."
}

# Define roles as skill requirements
roles = [
    "communication",
    "leadership",
    "data analysis",
    "attention to detail",
    "problem solving",
    "customer support"
]

# Load a sentence transformer model
model = SentenceTransformer('all-mpnet-base-v2')

# Embed roles
role_embeddings = model.encode(roles, convert_to_tensor=True)

# Create Q Matrix: similarity scores between agents and roles
q_matrix_data = {}
for agent_name, agent_text in agent_texts.items():
    agent_embedding = model.encode(agent_text, convert_to_tensor=True)
    similarity_scores = util.cos_sim(agent_embedding, role_embeddings)[0].cpu().tolist()
    q_matrix_data[agent_name] = similarity_scores

# Format as DataFrame
q_matrix = pd.DataFrame(q_matrix_data, index=roles).T
q_matrix = q_matrix.round(2)
print(q_matrix)
