# services/faiss_cache.py
import numpy as np
import faiss
from services.mongo.role_service import get_embedding, precompute_role_embeddings_with_faiss

role_name_faiss = None
faiss_index = None
text_to_role = None
roles_info_cache = None

async def initialize_faiss_and_embeddings(role_collection):
    global role_name_faiss, faiss_index, text_to_role, roles_info_cache
    roles_docs = await role_collection.find({}).to_list(length=None)
    roles_info_cache = {
        doc.get("name", ""): {"positive": doc.get("positive", [])}
        for doc in roles_docs
    }
    role_names = list(roles_info_cache.keys())
    role_name_embeddings = np.array([get_embedding(name) for name in role_names], dtype=np.float32)
    role_name_faiss = faiss.IndexFlatL2(role_name_embeddings.shape[1])
    role_name_faiss.add(role_name_embeddings)

    faiss_index, text_to_role = precompute_role_embeddings_with_faiss(roles_info_cache)
