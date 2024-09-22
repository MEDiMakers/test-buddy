import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, EarlyStoppingCallback
import torch

class LLM: 
    def __init__(self, tokenizer = "ethan-cyj/Cross-Encoder-Finetuned", model = "ethan-cyj/Cross-Encoder-Finetuned"): 
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.model = AutoModelForSequenceClassification.from_pretrained(model)
    
    def get_score(self,query, user_answer, threshold = 0.5):
        # Tokenize the input data
        inputs = self.tokenizer(query, user_answer, return_tensors='pt', truncation=True, padding=True)
        
        # Make predictions
        with torch.no_grad():
            logits = self.model(**inputs).logits

        # Apply sigmoid to get probabilities
        probabilities = torch.sigmoid(logits)
        predicted_class = 0
        if probabilities > threshold:
            return 1 
        else: 
            return predicted_class