\# 🌌 Research Assistant



An AI-powered research assistant built on first principles thinking. Upload a document, ask a question, and get a deep analytical response that connects root causes, patterns, and real-world implications.



\---



\## 🚀 What It Does



\- Accepts a user question and an optional document upload

\- Retrieves relevant knowledge from a RAG pipeline built on first principles thinking

\- Passes everything to a Google Gemini agent with a scientist-style analytical prompt

\- Returns a structured, deep analysis connecting fundamentals to the real world

\- Blocks prompt injection and harmful requests using HuggingFace toxic-bert

\- Permanently blacklists repeat offenders using SQLite



\---



\## 🛠️ Stack



| Layer | Technology |

|---|---|

| AI Agent | Pydantic AI + Google Gemini 2.5 Flash Lite |

| RAG Pipeline | LlamaIndex + HuggingFace Embeddings (BAAI) |

| Security | Transformers (toxic-bert) + SQLite blacklist |

| API | FastAPI + Uvicorn |

| Container | Docker |



\---



\## 📁 Project Structure



ResearchAssistant/

├── main.py                    # FastAPI app — connects everything

├── agent.py                   # Pydantic AI agent + Gemini model

├── RAG.py                     # LlamaIndex RAG pipeline

├── Security.py                # HuggingFace security + IP blacklisting

├── firstprinciplesthinking.txt # Knowledge base document

├── requirements.txt           # Dependencies

├── Dockerfile                 # Container configuration

└── .gitignore



\---



\## ⚙️ How To Run



\### Locally

```bash

pip install -r requirements.txt

uvicorn main:app --reload

```



\### With Docker

```bash

docker build -t research-assistant .

docker run -d `

&#x20; --name research-assistant-container `

&#x20; -p 8000:8000 `

&#x20; -v "${PWD}:/app" `

&#x20; -v "${HOME}/.cache/huggingface/hub:/root/.cache/huggingface/hub" ` # your hugging face model location (toxic-bert and BAAI)

&#x20; --env-file API\_KEY.env `

&#x20; \[DOCKER\_IMAGE\_NAME]

```



\### Test the API

```

http://127.0.0.1:8000/docs

```



\---



\## 🔐 Environment Variables



Create an `API\_KEY.env` file in the project root:

```

GOOGLE\_API\_KEY=your\_google\_api\_key

HF\_TOKEN=your\_huggingface\_token

```



Get your Google API key at \[aistudio.google.com](https://aistudio.google.com)

Get your HuggingFace token at \[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)



\---



\## 🌌 How It Works



```

User sends question + optional file

&#x20;           ↓

Middleware scans for prompt injection (toxic-bert)

&#x20;           ↓

IP blacklist check (SQLite)

&#x20;           ↓

RAG retrieves relevant chunks from knowledge base

&#x20;           ↓

Agent combines file + RAG context + question

&#x20;           ↓

Gemini returns structured first principles analysis

&#x20;           ↓

Response returned to user

```



\---



\## 👮‍♂️ Security Features



\- \*\*Prompt injection detection\*\* — HuggingFace toxic-bert scans every request

\- \*\*Confidence threshold\*\* — only blocks requests with 90%+ toxicity score to avoid false positives

\- \*\*IP violation tracking\*\* — in-memory counter per session

\- \*\*Permanent blacklisting\*\* — SQLite persists blacklisted IPs across server restarts

\- \*\*Misdirection response\*\* — blocked requests receive a fake maintenance message instead of an error



\---



\## 📄 License



MIT License — see \[LICENSE](LICENSE) for details.

