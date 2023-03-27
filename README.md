[![Banner](banner.png)](https://capsizegames.itch.io/chat-ai)

[![Upload Python Package](https://github.com/Capsize-Games/chatai/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Capsize-Games/chatai/actions/workflows/python-publish.yml)

# Chat AI: Run LLMs with your own hardware

Chat AI is an interface that sits on top of a custom engine which is responsible for processing requests and responses 
to and from an active Google T5-Flan model.

---

## Bundled Installation

[Official Build can be acquired here](https://capsizegames.itch.io/chat-ai) for those who want to use a compiled version of Chat AI without having to install any additional requirements

---

## Development

### Prerequisites

- Ubuntu 20.04+ or Windows 10+
- Python 3.10.6
- pip-23.0.1

#### Pypi installation

Use this installation method if you intend to use Chat AI from the command line or with
other python libraries or scripts.

`pip install chatairunner`

#### Development installation

Use this installation method if you intend to modify the source code of Chat AI.

- Ubuntu 20.04+ or Windows 10+
- Python 3.10.6
- pip-23.0.1

1. Fork this repo on github
2. `git clone https://github.com/Capsize-Games/chatai`
3. `cd chatai && pip install -r requirements.txt`
4. `python main.py`

