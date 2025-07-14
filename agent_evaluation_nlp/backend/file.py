import torch
from transformers import AutoTokenizer, AutoModel
import onnx

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")

model.eval()
dummy_input = tokenizer("Test input", return_tensors="pt")

torch.onnx.export(
    model,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "all_mpnet_base_v2.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["last_hidden_state", "pooler_output"],
    dynamic_axes={"input_ids": {0: "batch_size"}, "attention_mask": {0: "batch_size"}},
    opset_version=13
)

import onnx
onnx_model = onnx.load("all_mpnet_base_v2.onnx")
onnx.checker.check_model(onnx_model)