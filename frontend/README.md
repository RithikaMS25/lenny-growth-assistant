# Lenny Growth Assistant — Frontend

A React + Vite frontend for the Lenny Growth Assistant FastAPI backend.

## Prerequisites

- Node.js ≥ 18
- The FastAPI backend running (see backend instructions)

## Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env if your backend runs on a port other than 8000
```

### `.env` variables

| Variable             | Default                   | Description                                |
|----------------------|---------------------------|--------------------------------------------|
| `VITE_API_BASE_URL`  | `http://localhost:8000`   | Backend URL used in **production** builds. In development the Vite proxy handles this automatically — leave blank or set to your dev URL. |

## Development

```bash
npm run dev
```

Opens at **http://localhost:5173**. In dev mode, the Vite proxy forwards
`/api/*` and `/health/*` requests to the backend URL, so you won't hit CORS
issues.

**Backend must be running first.** If it isn't, the UI shows a clear
connection-error banner rather than a fake response.

## Production build

```bash
npm run build       # outputs to frontend/dist/
npm run preview     # local preview of the production bundle
```

Serve `dist/` with any static file server (Nginx, Caddy, etc.). Set
`VITE_API_BASE_URL` at build time to point at your deployed API.

## Features

| Feature | Status |
|---|---|
| Chat (POST /api/chat) | ✅ Wired to real backend |
| Source search (POST /api/search) | ✅ Wired to real backend |
| Backend health indicator | ✅ GET /health/ready |
| Session continuity (session_id reuse) | ✅ Preserved across messages |
| Provider indicator | ✅ Shown only when backend confirms |
| Source citations with similarity score | ✅ |
| Abstention state display | ✅ |
| Ship 30 for 30 essay feature | 🔜 UI shell built; backend endpoint not yet implemented |
| Document/artifact viewer | 🔜 Shell built; awaits backend output |

## Project structure

```
frontend/
├── src/
│   ├── services/
│   │   └── api.js          # All fetch calls; no mock responses
│   ├── hooks/
│   │   ├── useChatSession.js
│   │   └── useHealthCheck.js
│   ├── components/
│   │   ├── Sidebar.*
│   │   ├── StatusBar.*
│   │   ├── ChatView.*
│   │   ├── ChatMessage.*
│   │   ├── ChatInput.*
│   │   ├── SourcePanel.*
│   │   ├── SearchView.*
│   │   ├── Ship30View.*
│   │   └── ArtifactView.*
│   ├── App.jsx
│   ├── App.module.css
│   ├── index.css           # Global design tokens
│   └── main.jsx
├── .env.example
├── .env
└── vite.config.js
```

## Backend CORS

If you deploy the frontend on a different origin than the backend, add CORS
middleware to the FastAPI app:

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
