# 🏥 HCPilot AI

### AI-First CRM for Intelligent Healthcare Professional Engagement

An AI-powered Customer Relationship Management system designed for pharmaceutical field representatives. Instead of manually filling CRM forms, representatives simply describe their interactions in natural language — the AI automatically extracts structured data and populates the form.

![Tech Stack](https://img.shields.io/badge/React-TypeScript-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Python-green) ![LangGraph](https://img.shields.io/badge/LangGraph-AI_Agent-purple) ![Groq](https://img.shields.io/badge/Groq-Gemma2_9B-orange)

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **AI Chat Interface** | Describe meetings naturally, AI fills the form |
| **Auto Form Population** | Extracts HCP name, date, sentiment, products, etc. |
| **Smart Editing** | Say "change the sentiment to negative" — only that field updates |
| **Natural Search** | "Show all meetings with Dr. Sharma" |
| **Follow-up Suggestions** | AI recommends next actions based on context |
| **Interaction Summary** | Get executive summaries of your HCP relationships |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React + TypeScript, Redux Toolkit, Vanilla CSS |
| **Backend** | Python, FastAPI, SQLAlchemy |
| **AI Agent** | LangGraph (5 tools), LangChain |
| **LLM** | Groq API — Gemma2-9B-IT |
| **Database** | SQLite (default) / PostgreSQL |
| **Font** | Google Inter |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│  ┌──────────────┐         ┌──────────────────────────┐  │
│  │  Form Panel  │         │    AI Chat Panel         │  │
│  │  (Read-only) │◄───────►│  (User ↔ AI messages)    │  │
│  └──────────────┘  Redux  └──────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ POST /api/chat
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │              LangGraph Agent                     │    │
│  │  START → Intent Classifier → Tool Router         │    │
│  │                                ├─ Log Interaction │    │
│  │                                ├─ Edit Interaction│    │
│  │                                ├─ Search          │    │
│  │                                ├─ Follow-up       │    │
│  │                                └─ Summary         │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                               │
│  ┌──────────┐    ┌──────┴──────┐                        │
│  │ Groq LLM │    │  Database   │                        │
│  │ Gemma2-9B│    │  SQLite/PG  │                        │
│  └──────────┘    └─────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ LangGraph Tools

### Tool 1: Log Interaction (Mandatory)
Extracts structured CRM data from natural language meeting descriptions.
```
Input:  "Met Dr. Sharma today, discussed CardioX, positive sentiment, shared brochures"
Output: {hcp_name: "Dr. Sharma", sentiment: "Positive", products: "CardioX", materials: "Brochures", ...}
```

### Tool 2: Edit Interaction (Mandatory)
Modifies only the specified fields while preserving everything else.
```
Input:  "Actually the name was Dr. John and sentiment was negative"
Output: Updates ONLY hcp_name and sentiment fields
```

### Tool 3: Search Interaction
Natural language search across interaction history.
```
Input:  "Show all meetings with Dr. Sharma"
Output: List of matching interactions with details
```

### Tool 4: Generate Follow-up
AI-generated next-step recommendations based on interaction context.
```
Input:  "Suggest follow-up for my last meeting"
Output: Recommended date, actions, talking points, materials
```

### Tool 5: Interaction Summary
Executive summary of HCP relationship and meeting history.
```
Input:  "Summarize my interactions with Dr. Sharma"
Output: Comprehensive summary with sentiment trends and insights
```

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Groq API Key** from [console.groq.com](https://console.groq.com)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/hcpilot-ai.git
cd hcpilot-ai
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Seed the database (optional)
python seed_data.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Open the Application
Navigate to **http://localhost:5173** in your browser.

---

## 📁 Project Structure

```
HCPilot AI/
├── frontend/                   # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── FormPanel/      # Read-only CRM form
│   │   │   └── ChatPanel/      # AI assistant chat
│   │   ├── redux/
│   │   │   ├── store.ts
│   │   │   ├── interactionSlice.ts
│   │   │   └── chatSlice.ts
│   │   ├── services/api.ts     # Backend API calls
│   │   ├── types/index.ts      # TypeScript definitions
│   │   └── App.tsx             # Main layout
│   └── package.json
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── database.py         # SQLAlchemy setup
│   │   ├── models/             # Database models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── api/                # Route handlers
│   │   └── agent/              # LangGraph agent
│   │       ├── graph.py        # Agent graph definition
│   │       ├── state.py        # Shared state
│   │       ├── router.py       # Intent classifier
│   │       ├── nodes.py        # Graph nodes
│   │       └── tools/          # 5 LangGraph tools
│   ├── seed_data.py
│   ├── requirements.txt
│   └── .env
├── .info/                      # Project documentation
├── README.md
└── .gitignore
```

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message to AI agent |
| `GET` | `/api/interactions` | List all interactions |
| `GET` | `/api/interactions/{id}` | Get single interaction |
| `POST` | `/api/interactions` | Create interaction |
| `PUT` | `/api/interactions/{id}` | Update interaction |
| `GET` | `/api/hcps` | List all HCPs |
| `GET` | `/api/health` | Health check |

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM access | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./hcpilot.db` |

---

## 📄 License

This project is developed as part of an AI-First CRM assignment.
