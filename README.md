[![Banner](banner.png)](https://capsizegames.itch.io/chat-ai)

# Chat AI: Run LLMs with your own hardware

Chat AI is an interface that sits on top of a custom engine which is responsible for processing requests and responses 
to and from an active Google T5-Flan model.

---

## Dev Setup

### Installation

#### Prerequisites

- Ubuntu 20.04+ or Windows 10+
- Python 3.10.6
- pip-23.0.1

#### For development on Chat AI

1. Create venv `python -m venv venv`
2. Clone [aiengine](https://github.com/Capsize-Games/chat-ai)
3. `cd aiengine && pip install -r requirements.txt`

Chat AI is built on top of sdrunner which is responsible for handling the model's input and output sdrunner can be found here.

#### Running the application

```
python main.py
```

---

## API

1. `pip install chatai`
2. `from chatai import ChatAI`
3. `ai = ChatAI()`

### Query the API 

`ai.query(query="Hello, how are you?", type="chat", botname="ChatBot", username="User")`
