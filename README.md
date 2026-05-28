<p align="center">
  <h1 align="center">SceneTalk</h1>
  <p align="center">AI-Powered English Oral Practice Platform</p>
</p>

---

## Overview

SceneTalk is an immersive, scene-based English speaking practice platform with AI-powered conversational memory, full voice interaction, bilingual translation, and vocabulary lookup. It supports **17 real-life scenarios** — from restaurants and interviews to travel and medical visits — giving learners a realistic environment to build oral fluency.

---

## Features

### Scene-Based Dialogue
- 17 high-frequency scenarios with dedicated AI role-play (waiter, interviewer, doctor, guide, etc.)
- Scene-specific opening lines and AI personas for authentic conversation flow
- Scene switching auto-resets context to avoid cross-scene interference

### Contextual Memory
- Powered by **ChromaDB** for persistent conversation memory
- AI responses are context-aware, enabling natural multi-turn dialogue
- Scene-isolated memory ensures conversations stay on-topic

### Full Voice Interaction
- **Speech-to-Text**: Real-time microphone input for hands-free speaking practice
- **Text-to-Speech**: AI replies are auto-read aloud with natural pronunciation
- **Replay**: Click any sentence bubble to replay its audio — perfect for shadowing practice

### Bilingual Side-by-Side Translation
- Real-time Chinese-English parallel translation display
- Side-by-side layout: dialogue on the left, translations on the right

### Listening & Pronunciation
- Dedicated **Listening Practice** module with structured exercises
- **Sentence Analysis** with detailed breakdowns
- **Linking Rules** reference for connected speech patterns

### Word Tools
- **Quick Word Lookup**: Search any word for phonetics and Chinese definitions
- **Word Notebook**: Save and review vocabulary collected during practice

---

## Pages

| Page | Path | Description |
|------|------|-------------|
| Practice | `/` | Main oral practice — scene selection, AI chat, TTS/ASR |
| Listening | `/listening` | Structured listening comprehension exercises |
| Dialogues | `/dialogues` | Browse and study example dialogues by scene |
| Sentences | `/sentences` | In-depth sentence analysis and breakdown |
| Linking Rules | `/linking-rules` | Pronunciation linking and connected speech guide |
| Notes | `/notes` | Saved word notebook for vocabulary review |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, React Router |
| **Backend** | Python FastAPI, Uvicorn |
| **Vector Memory** | ChromaDB |
| **AI / LLM** | DeepSeek API, DashScope (Qwen) |
| **Speech** | Edge-TTS (synthesis), ASR service (recognition) |
| **Database** | MySQL (aiomysql), local JSON/file storage |
| **Audio** | Server-side audio processing & storage |

---

## Project Structure

```
oral-practice/
├── frontend/               # React + TypeScript + Vite
│   └── src/
│       ├── pages/          # 6 page modules
│       ├── components/     # Reusable UI components
│       ├── hooks/          # Custom React hooks
│       ├── services/       # API client layer
│       └── assets/         # Static assets
├── backend/                # Python FastAPI
│   ├── main.py             # App entry point
│   ├── config.py           # Configuration & scene definitions
│   ├── routers/            # API route handlers
│   ├── services/           # AI, TTS, ASR, audio, storage
│   ├── scripts/            # Data generation & ETL scripts
│   └── data/               # Runtime data & ChromaDB persistence
├── start.bat               # Windows quick-start launcher
└── start.ps1               # PowerShell quick-start launcher
```

---

## Getting Started

### Prerequisites
- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **MySQL** (for listening data; fallback to local storage for other modules)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure your API keys in backend/.env:
#   DASHSCOPE_API_KEY=your_key
#   DEEPSEEK_API_KEY=your_key
#   DB_HOST=...  DB_USER=...  DB_PASSWORD=...  DB_NAME=...

python main.py
# API server runs at http://127.0.0.1:8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Dev server runs at http://localhost:5173
```

### Quick Start (Windows)

Run `start.bat` or `start.ps1` to launch both frontend and backend simultaneously.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
