# 🧠 Multimodal Q&A Pro

🚀 **Live Deployment Link**: [https://multimodal-qa-pro.onrender.com](https://multimodal-qa-pro.onrender.com)

**One Agent. Three Senses. — A Hybrid RAG System with Document Search, Web Search & Vision.**

Multimodal Q&A Pro is a full-stack AI-powered question-answering platform built for the **GenAI Summer of Code Hackathon 2026**. It combines local document retrieval (RAG), real-time web search, and image understanding into a single intelligent agent — all wrapped in a sleek, modern web interface.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-6.x-FF6F00?logo=gradio&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.3-1C3C3C?logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2-blue)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-F55036)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 📄 **PDF Document Search (RAG)** | Upload PDFs → auto-chunked, embedded & indexed into an optimized SQLite Text Store. Query them with natural language. |
| 🌐 **Real-time Web Search** | Fetches live results from DuckDuckGo for current events, news, and general knowledge. |
| 🖼️ **Image Understanding** | Upload images → analyzed using Groq's vision-capable LLM (LLaMA 3.3 70B). |
| 🤖 **Hybrid Agent Routing** | LangGraph ReAct agent automatically decides which tool(s) to use based on the query. |
| 🔐 **User Authentication** | Full signup/login system with bcrypt-hashed passwords and SQLite storage. |
| 🎨 **Modern UI** | Claude-inspired dark theme with sidebar, animated landing page, and responsive layout. |
| 🔄 **Automatic Fallback** | If the primary model fails, the agent falls back to `llama-3.1-8b-instant` automatically. |


---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Gradio 6)                       │
│  ┌──────────┐  ┌───────────────────────────┐  ┌──────────────┐  │
│  │ Landing   │  │    Workspace (Chat UI)    │  │  Login/Signup │  │
│  │   Page    │  │  Sidebar + Chatbot + Input│  │    Pages     │  │
│  └──────────┘  └───────────────────────────┘  └──────────────┘  │
│                        FastAPI (uvicorn)                          │
├──────────────────────────┬──────────────────────────────────────┤
│                          │                                      │
│              BACKEND INTERFACE (backend_interface.py)            │
│                          │                                      │
│  ┌───────────────────────┼──────────────────────────────────┐   │
│  │              LangGraph ReAct Agent (agent.py)             │   │
│  │                       │                                   │   │
│  │    ┌──────────┐  ┌────┴─────┐  ┌──────────────┐         │   │
│  │    │ Document  │  │   Web    │  │    Image     │         │   │
│  │    │  Search   │  │  Search  │  │  Description │         │   │
│  │    │(ChromaDB) │  │(DuckDuck)│  │ (Groq Vision)│         │   │
│  │    └──────────┘  └──────────┘  └──────────────┘         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                      │
│  ┌───────────────────────┼──────────────────────────────────┐   │
│  │                  DATA LAYER                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────────┐     │   │
│  │  │ ChromaDB  │  │ SQLite   │  │ Sentence           │     │   │
│  │  │(Vectors)  │  │(Users DB)│  │ Transformers       │     │   │
│  │  └──────────┘  └──────────┘  │ (Embeddings)       │     │   │
│  │                              └────────────────────┘     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
multimodal-qa-pro/
├── app.py                     # Main application — Gradio UI + FastAPI server
├── agent.py                   # LangGraph ReAct agent with tool routing
├── auth.py                    # User authentication (signup/login with bcrypt + SQLite)
├── backend_interface.py       # Bridge between frontend and backend agent/tools
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (GROQ_API_KEY)
├── .gitignore                 # Git ignore rules
│
├── tools/                     # LangChain tool implementations
│   ├── doc_search.py          #   → ChromaDB document search tool
│   ├── web_search.py          #   → DuckDuckGo web search tool
│   ├── image_tool.py          #   → Groq Vision image description tool
│   └── safe_call.py           #   → Error-handling decorator for tools
│
├── vectorstore/               # Vector store utilities
│   └── chroma_utils.py        #   → PDF chunking, embedding & ChromaDB indexing
│
├── chroma_db/                 # ChromaDB persistent storage (auto-generated)
└── users.db                   # SQLite user database (auto-generated)
```

---

## 🔧 Backend — In Detail

### 1. Agent (`agent.py`)

The brain of the application — a **LangGraph ReAct agent** that reasons about which tools to invoke:

- **Primary LLM**: `llama-3.3-70b-versatile` via Groq API (fast inference, zero temperature for determinism)
- **Fallback LLM**: `llama-3.1-8b-instant` (auto-triggers if the primary model hits Groq API parser limitations)
- **Framework**: LangGraph's `create_react_agent` — a reasoning-and-acting loop that:
  1. Reads the user query
  2. Decides which tool(s) to call (or none)
  3. Executes the tool(s)
  4. Synthesizes a final answer with source citations
- **Recursion Limit**: 12 steps max to prevent infinite loops

### 2. Tools (`tools/`)

| Tool | File | Description |
|------|------|-------------|
| `search_documents` | `doc_search.py` | Queries the local ChromaDB vector store for semantically relevant chunks from uploaded PDFs. Uses `sentence-transformers` embeddings. Returns top-k matching passages with metadata. |
| `search_web` | `web_search.py` | Performs real-time web searches using the DuckDuckGo Search API (`ddgs`). Returns summarized results for current events, news, and general knowledge questions. |
| `describe_image` | `image_tool.py` | Sends images to Groq's vision-capable LLM for analysis. Encodes images as base64, handles multiple formats (PNG, JPEG, etc.), returns detailed natural language descriptions. |
| `safe_call` | `safe_call.py` | A decorator that wraps tool functions with error handling, returning clean failure messages instead of crashing the agent. |

### 3. Vector Store (`vectorstore/chroma_utils.py`)

- **PDF Processing Pipeline**:
  1. Extracts text from PDFs using `pypdf`
  2. Splits into chunks using LangChain's `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap)
  3. Generates embeddings via `sentence-transformers` (HuggingFace)
  4. Stores in ChromaDB with persistent local storage (`./chroma_db/`)
- **Similarity Search**: Cosine similarity over embedded chunks, returns top relevant passages

### 4. Authentication (`auth.py`)

- **Database**: SQLite (`users.db`) with auto-initialization
- **Password Security**: Bcrypt hashing with salt
- **Validation**: Email format checks, minimum 8-character passwords, duplicate email detection
- **API Endpoints** (via FastAPI):
  - `POST /api/login` — Authenticate existing users
  - `POST /api/signup` — Register new users

### 5. Backend Interface (`backend_interface.py`)

Clean bridge layer between the Gradio frontend and backend systems:
- `process_pdf(file_path)` → Indexes PDF into ChromaDB, returns chunk count
- `process_image(image_path)` → Sends to Groq Vision, returns description
- `run_agent_query(query)` → Invokes the ReAct agent, returns answer + tools trace

---

## 🎨 Frontend — In Detail

### Built with Gradio 6 + Custom CSS + FastAPI

The frontend is a **single-page application** with three views:

### 1. Landing Page
- Fully custom HTML/CSS/JS (injected via iframe)
- **Animated grid background** with CSS gradient patterns
- **Scroll-triggered reveal animations** using `IntersectionObserver`
- **Magnetic hover effects** on interactive elements
- **Dark/Light theme toggle** with smooth transitions
- Feature showcase cards with icons and descriptions
- "Get Started" CTA button → navigates to Login

### 2. Login / Signup Page
- Custom HTML/CSS form (injected via iframe)
- Tab-based toggle between Login and Signup forms
- Client-side validation with animated error messages
- Communicates with Gradio backend via `postMessage` API
- Frosted glass (glassmorphism) card design

### 3. Workspace (Chat Interface)
- **Claude-inspired layout**:
  - **Left Sidebar** (260px): Logo, "+ New chat" button, chat history area, user profile with avatar
  - **Main Chat Area**: Full-height chatbot with auto-scroll
  - **Input Bar**: Pill-shaped search bar with:
    - 📎 Upload PDF/Image button (left)
    - Text input with placeholder (right)
    - Focus glow effect with accent color
- **Design System**:
  - CSS custom properties (variables) for theming
  - `Inter` font for body, `Space Grotesk` for headings
  - Dark mode by default with carefully tuned color palette
  - Responsive layout with flexbox
  - Smooth transitions and hover effects throughout

### CSS Architecture
- Full viewport lock (`100vh`, `overflow: hidden`) — no browser scrollbars
- Nested flex containers to ensure sidebar + chat fill the entire screen
- Custom styling overrides for Gradio's internal components (`.form`, `.contain`, `.wrap`)
- Message bubbles with distinct styles for user (accent blue) and bot (surface card)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- A [Groq API Key](https://console.groq.com/) (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/Akshay111962/multimodal-qa-pro.git
cd multimodal-qa-pro

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo GROQ_API_KEY=your_groq_api_key_here > .env

# Run the application
python app.py
```

The app will start at **http://localhost:7860**

---

## ☁️ Deployment (Render)

This app is configured for deployment on [Render](https://render.com) (free tier):

| Setting | Value |
|---------|-------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Environment Variable** | `GROQ_API_KEY` = your key |

The app reads the `PORT` environment variable automatically for Render compatibility.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq API — LLaMA 3.3 70B Versatile (+ 8B fallback) |
| **Agent Framework** | LangGraph (ReAct pattern) |
| **Tool Orchestration** | LangChain Core |
| **Vector Database** | ChromaDB (persistent, local) |
| **Embeddings** | Sentence Transformers (HuggingFace) |
| **Web Search** | DuckDuckGo Search API |
| **Frontend** | Gradio 6 + Custom HTML/CSS/JS |
| **Backend Server** | FastAPI + Uvicorn |
| **Authentication** | SQLite + bcrypt |
| **PDF Parsing** | PyPDF |
| **Image Processing** | Pillow + base64 encoding |

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Akshay Purohit . Achyut Pathak**

Built for the GenAI Summer of Code Hackathon 2026.
