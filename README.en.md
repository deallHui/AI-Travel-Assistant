# AI Travel Assistant

An intelligent travel Q&A and itinerary planning system powered by RAG retrieval and LLM reasoning. It offers destination recommendations, itinerary planning, traffic guidance, and budget advice with multi‑client support.

## Highlights

- Intelligent travel Q&A and guide search
- Itinerary planning and route suggestions
- Destination and attraction recommendations
- Accommodation, food, traffic, and budget guidance
- Frontend/backend separation with Web and mini‑program clients

## Tech Stack

- Backend: FastAPI + LangChain + ChromaDB
- Frontend: React + Vite + Ant Design
- Mini Program: WeChat Mini Program (WCDS)
- Model: DeepSeek and other LLM integrations

## Project Structure

```
AICD2/
├── rag_ai/                 # RAG assistant module
│   ├── backend/            # Backend service
│   ├── frontend/           # Web frontend
│   ├── vectorstores/       # Vector database
│   └── requirements.txt    # Python dependencies
├── WCDS/                   # WeChat mini program client
├── src/                    # Other service code (Java)
├── README.md
└── README.en.md
```

## Quick Start (RAG Module)

### 1. Requirements

- Python 3.8+
- Node.js 16+

### 2. Configure Environment Variables

Copy the sample file and fill in your key:

```bash
copy rag_ai\backend\.env.example rag_ai\backend\.env
```

Edit `rag_ai/backend/.env`:

```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r rag_ai/requirements.txt
cd rag_ai/frontend
npm install
```

### 4. Start Services

```bash
python rag_ai/start_backend.py
rag_ai\start_frontend.bat
```

Access URLs:

- Web UI: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Mini Program (WCDS)

Open `WCDS/` with WeChat DevTools to run. Deployment notes can be found in the `WCDS/` docs.

## Contributing

Issues and Pull Requests are welcome.
