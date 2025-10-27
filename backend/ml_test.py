import os
import torch
from transformers import pipeline

print('Torch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())

model_name = 'cardiffnlp/twitter-roberta-base-sentiment-latest'
print('Loading sentiment pipeline for model:', model_name)

try:
    device = 0 if torch.cuda.is_available() else -1
    sentiment = pipeline('sentiment-analysis', model=model_name, device=device)
    res = sentiment('I love this project!')[0]
    print('Inference result:', res)
except Exception as e:
    print('Model load/inference failed:', e)
