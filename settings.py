TEXT_MODELS = {
    "flan-t5-xxl": {
        "path": "google/flan-t5-xxl",
        "class": "AutoModelForSeq2SeqLM",
        "tokenizer": "AutoTokenizer",
    },
    "flan-t5-xl": {
        "path": "google/flan-t5-xl",
        "class": "AutoModelForSeq2SeqLM",
        "tokenizer": "AutoTokenizer",
    },
    "flan-t5-large": {
        "path": "google/flan-t5-large",
        "class": "AutoModelForSeq2SeqLM",
        "tokenizer": "AutoTokenizer",
    },
    "flan-t5-small": {
        "path": "google/flan-t5-small",
        "class": "AutoModelForSeq2SeqLM",
        "tokenizer": "AutoTokenizer",
    },
    "flan-t5-base": {
        "path": "google/flan-t5-base",
        "class": "AutoModelForSeq2SeqLM",
        "tokenizer": "AutoTokenizer",
    },
    "DialoGPT-large": {
        "path": "microsoft/DialoGPT-large",
        "class": "AutoModelForCausalLM",
        "tokenizer": "AutoTokenizer",
    }
}
VERSION = "1.0.0"