import onnxruntime
from transformers import AutoTokenizer
_model = None

def get_onnx_session(path="agent_evaluation_nlp/backend/all_mpnet_base_v2.onnx"):
    global _model
    if _model is None:
        print("🚀 Loading ONNX model...")
        _model = onnxruntime.InferenceSession(path)
    return _model

_tokenizer = None

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        print("🧠 Loading tokenizer...")
        _tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
    return _tokenizer