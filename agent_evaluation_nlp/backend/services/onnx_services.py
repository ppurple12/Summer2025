import onnxruntime
import os
import urllib.request

# Define local file names
MODEL_PATH = "all_mpnet_base_v2.onnx"
MLP_PATH = "mlp_model.onnx"

# Define remote URLs
MODEL_URL = "https://huggingface.co/pppurple12/embedding_model/resolve/main/all_mpnet_base_v2.onnx"
MLP_URL = "https://huggingface.co/pppurple12/embedding_model/resolve/main/mlp_model.onnx"

_ort_session = None
_mlp_session = None

def download_if_missing(file_path, url):
    if not os.path.exists(file_path):
        print(f"⬇️ Downloading {file_path} from {url}...")
        urllib.request.urlretrieve(url, file_path)
        print(f"✅ Downloaded {file_path}.")

def get_ort_session():
    global _ort_session
    if _ort_session is None:
        download_if_missing(MODEL_PATH, MODEL_URL)
        print("🧠 Loading ONNX embedding model...")
        _ort_session = onnxruntime.InferenceSession(MODEL_PATH)
    return _ort_session

def get_mlp_session():
    global _mlp_session
    if _mlp_session is None:
        download_if_missing(MLP_PATH, MLP_URL)
        print("📈 Loading ONNX MLP model...")
        _mlp_session = onnxruntime.InferenceSession(MLP_PATH)
    return _mlp_session