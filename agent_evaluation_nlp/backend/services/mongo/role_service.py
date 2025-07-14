import numpy as np
import faiss
#from sentence_transformers import SentenceTransformer
import onnxruntime
from transformers import AutoTokenizer
import os
print("Current dir:", os.getcwd())
print("Model path exists:", os.path.exists("backend/all_mpnet_base_v2.onnx"))
print("Model path exists:", os.path.exists("backend/all_mpnet_base_v2.onnx"))
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
def get_embedding(text):
    if text not in embedding_cache:
        embedding_cache[text] = onnx_embed(text)[0]
    return embedding_cache[text]


# precompute role embeddings with FAISS
def precompute_role_embeddings_with_faiss(roles_info):
    role_embeddings = []
    text_to_role = []
    seen_texts = {}

    for role_name, role_info in roles_info.items():
        keywords = [role_name] + role_info.get("positive", [])
        for text in keywords:
            if text not in seen_texts:
                vec = get_embedding(text)
                seen_texts[text] = vec
                role_embeddings.append(vec)
                text_to_role.append((text, role_name))  # for reverse lookup

    dim = len(role_embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(role_embeddings).astype(np.float32))

    return index, text_to_role

async def add_keyword_mongo(keyword: str, matched_role: str, role_collection):

    # Fetch matched role document
    role_doc = await role_collection.find_one({"name": matched_role})
    if not role_doc:
        print(f"Role '{matched_role}' not found in MongoDB.")
        return None

    positive_keywords = role_doc.get("positive", [])

    # 1. Exact match check (case-insensitive)
    if any(keyword.lower() == kw.lower() for kw in positive_keywords):
        print(f"Keyword '{keyword}' exactly exists in positive list of role '{matched_role}'")
        return matched_role

    # 2. Semantic similarity check with FAISS on positive keywords of this role
    if positive_keywords:
        # Embed all positive keywords of the role
        positive_vecs = np.array([get_embedding(kw) for kw in positive_keywords]).astype(np.float32) 
        # Build FAISS index for these vectors
        import faiss
        dim = positive_vecs.shape[1]
        faiss_index = faiss.IndexFlatL2(dim)
        faiss_index.add(positive_vecs)

        # Embed the input keyword
        keyword_vec = get_embedding(keyword).astype(np.float32).reshape(1, -1)

        # Search nearest neighbor
        D, I = faiss_index.search(keyword_vec, 1)
        distance = D[0][0]

        SIMILARITY_THRESHOLD = 0.5  # tune this threshold as needed
        if distance < SIMILARITY_THRESHOLD:
            similar_kw = positive_keywords[I[0][0]]
            print(f"Keyword '{keyword}' semantically similar to existing positive keyword '{similar_kw}' (distance={distance:.4f})")
            return matched_role

    # 3. If no exact or similar found, add keyword to MongoDB positive list
    await role_collection.update_one(
        {"name": matched_role},
        {"$addToSet": {"positive": keyword}},
        upsert=True
    )
    print(f"Keyword '{keyword}' added to role '{matched_role}'")
    return matched_role