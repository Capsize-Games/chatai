from datasets import load_dataset

from transformers import pipeline
from random import randrange
dataset_id = "samsum"
dataset = load_dataset(dataset_id)
# load model and tokenizer from huggingface hub with pipeline
summarizer = pipeline("summarization", model="/home/joe/PycharmProjects/sdrunner.py/local/flan-t5-large-samsum", device=0)

# select a random test sample
sample = dataset['test'][42]
print(f"dialogue: \n{sample['dialogue']}\n---------------")

# summarize dialogue
res = summarizer(sample["dialogue"])

print(f"flan-t5-base summary:\n{res[0]['summary_text']}")
