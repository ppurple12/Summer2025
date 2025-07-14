import onnxruntime
import os

MODEL_PATH = "backend/all_mpnet_base_v2.onnx"
MLP_PATH = "mlp_model.onnx"

_ort_session = None
_mlp_session = None

def get_ort_session():
    global _ort_session
    if _ort_session is None:
        print("🧠 Loading ONNX embedding model...")
        _ort_session = onnxruntime.InferenceSession(MODEL_PATH)
    return _ort_session

def get_mlp_session():
    global _mlp_session
    if _mlp_session is None:
        print("📈 Loading ONNX MLP model...")
        _mlp_session = onnxruntime.InferenceSession(MLP_PATH)
    return _mlp_session