# Pocket Joe App Template

A minimal template for building **MCP tools**, **FastAPI endpoints**, and a **frontend UI** — all in one repo, deployable to **Railway** (backend) + **Vercel/Netlify** (frontend).

This template uses:
- MCP tool: **hello_world_policy**
- FastAPI: `/api/hello`
- MCP endpoint: `/mcp`
- Frontend: single textbox → calls API → shows response

---

# 1. Repository Layout

```
pocket-joe-app-template/
├── server.py          # MCP + FastAPI backend
├── pyproject.toml
├── uv.lock
├── railway.json       # Railway deployment config
├── .gitignore
└── frontend/          # Vite/React/Tailwind UI
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── .env.example
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts
        └── index.css
```

---

# 2. Backend – MCP + FastAPI

## 2.1 `pyproject.toml`

```toml
[project]
name = "pocket-joe-app-template"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pocket-joe>=0.1.0.3",
    "fastmcp>=2.0.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
]
```

---

## 2.2 `server.py` — minimal Hello World MCP + API

```python
#!/usr/bin/env python3
"""Pocket Joe App Template – MCP + FastAPI"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from pocket_joe import BaseContext, InMemoryRunner, Message, policy

# ───────────────────────────────────────────────────────────────
# MCP TOOL – hello_world_policy
# Takes an optional input string → returns "hello {input or 'world'}"
# ───────────────────────────────────────────────────────────────

@policy.tool(description="Return a hello greeting. Optional input.")
async def hello_world_policy(text: str | None = None) -> list[Message]:
    greeting = f"hello {text if text else 'world'}"
    return [
        Message(
            id="",
            actor="hello_world_policy",
            type="action_result",
            payload={"greeting": greeting},
        )
    ]


# ───────────────────────────────────────────────────────────────
# POCKET-JOE CONTEXT
# Binds policies for use in workflows. Extend this as you add
# more policies to your app.
# ───────────────────────────────────────────────────────────────
class AppContext(BaseContext):
    def __init__(self, runner):
        super().__init__(runner)
        self.hello = self._bind(hello_world_policy)

runner = InMemoryRunner()
ctx = AppContext(runner)

# ───────────────────────────────────────────────────────────────
# MCP SERVER
# Exposes policies as MCP tools. Mounted under /mcp
# Note: We register the same function to both pocket-joe (@policy.tool)
# and FastMCP (mcp.tool) for dual-interface support.
# ───────────────────────────────────────────────────────────────
mcp = FastMCP("pocket-joe-app-template")
mcp.tool(hello_world_policy)
mcp_app = mcp.http_app(path="/mcp")

# ───────────────────────────────────────────────────────────────
# FASTAPI APP (API + MCP Mount + CORS)
# ───────────────────────────────────────────────────────────────
app = FastAPI(title="Pocket Joe App Template", lifespan=mcp_app.lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # local frontend (Vite dev)
        "https://YOUR-VERCEL-APP.vercel.app",  # TODO: replace with your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP → /mcp
app.mount("/mcp", mcp_app)


# ────────────────────────────────────────────────
# FastAPI Endpoint: /api/hello
# REST mirror of the MCP tool for direct HTTP access
# ────────────────────────────────────────────────
@app.get("/api/hello")
async def hello_api(text: str | None = Query(None)):
    msgs = await hello_world_policy(text)
    return msgs[0].payload


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {
        "message": "Pocket Joe App Template",
        "endpoints": {
            "api": "/api/hello?text=joe",
            "mcp": "/mcp",
            "health": "/health",
        },
    }
```

---

## 2.3 `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.env

# uv
.python-version

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Frontend (if in same repo)
frontend/node_modules/
frontend/dist/
frontend/.env.local
```

---

## 2.4 `railway.json`

```json
{
  "$schema": "https://railway.com/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30
  }
}
```

---

## 2.5 Run locally

```bash
uv sync
uv run uvicorn server:app --reload --port 8000
```

Test:
- `http://localhost:8000/` → API info
- `http://localhost:8000/api/hello` → `{"greeting": "hello world"}`
- `http://localhost:8000/api/hello?text=joe` → `{"greeting": "hello joe"}`
- `http://localhost:8000/health` → `{"status": "ok"}`
- MCP endpoint → `http://localhost:8000/mcp`

---

# 3. Railway Deployment

1. Push repo to GitHub
2. Go to [Railway Dashboard](https://railway.app/dashboard)
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repo — Railway auto-detects Python via `pyproject.toml`
5. Wait for deployment (~2-3 minutes)
6. Copy the generated URL (e.g., `https://your-app.railway.app`)
7. Use this URL as `VITE_API_BASE_URL` for the frontend

---

# 4. Frontend – Vite + React + Tailwind

## 4.1 Create frontend

```bash
mkdir frontend && cd frontend
npm create vite@latest . -- --template react-ts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## 4.2 Config files

### `tailwind.config.js`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

### `postcss.config.js`

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### `.env.example`

```bash
# Backend API URL
# For local development, leave unset (defaults to http://localhost:8000)
# For production, set to your Railway URL
VITE_API_BASE_URL=https://your-app.railway.app
```

---

## 4.3 `src/api.ts`

```ts
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type HelloResponse = { greeting: string };

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function sayHello(text?: string): Promise<HelloResponse> {
  const params = new URLSearchParams();
  if (text) params.set("text", text);

  const url = `${API_BASE}/api/hello?${params.toString()}`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new ApiError(
      `API request failed: ${res.status} ${res.statusText}`,
      res.status,
      res.statusText
    );
  }

  return res.json();
}
```

---

## 4.4 `src/main.tsx`

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

---

## 4.5 `src/App.tsx`

```tsx
import { useState } from "react";
import { sayHello, HelloResponse, ApiError } from "./api";

export default function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState<HelloResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await sayHello(input);
      setResponse(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Error ${err.status}: ${err.statusText}`);
      } else {
        setError("Failed to connect to API");
      }
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-6">
      <div className="max-w-md w-full bg-slate-800 p-6 rounded-xl shadow-lg space-y-4">
        <h1 className="text-2xl font-bold">Pocket Joe App Template</h1>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            className="w-full p-2 rounded bg-slate-700 border border-slate-600 focus:border-emerald-500 focus:outline-none"
            placeholder="Type something…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-800 text-black py-2 rounded font-semibold transition-colors"
          >
            {loading ? "Loading…" : "Say Hello"}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded text-red-200">
            {error}
          </div>
        )}

        {response && (
          <div className="mt-4 p-4 bg-slate-700 rounded">
            {response.greeting}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 4.6 Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`

---

# 5. Vercel/Netlify Deployment (Frontend)

## Vercel

1. Push `frontend/` to GitHub (or as subdirectory)
2. Import to Vercel
3. Set **Root Directory** to `frontend`
4. Add environment variable:
   - `VITE_API_BASE_URL` = `https://your-app.railway.app`
5. Deploy

## Netlify

1. Push to GitHub
2. Import to Netlify
3. **Base directory**: `frontend`
4. **Build command**: `npm run build`
5. **Publish directory**: `frontend/dist`
6. Add environment variable `VITE_API_BASE_URL`

---

# 6. Use MCP in Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pocket-joe-app": {
      "url": "https://your-app.railway.app/mcp"
    }
  }
}
```

Restart Claude Desktop — the `hello_world_policy` tool will be available.

---

# 7. Adding More Tools

1. Create your policy function with `@policy.tool` decorator
2. Add to `AppContext` with `self._bind(YourPolicy)`
3. Register with FastMCP: `mcp.tool(your_policy)`
4. Optionally add a REST endpoint in FastAPI
5. Push to GitHub — Railway auto-deploys

Example:

```python
@policy.tool(description="Reverse the input text")
async def reverse_policy(text: str) -> list[Message]:
    return [
        Message(
            id="",
            actor="reverse_policy",
            type="action_result",
            payload={"reversed": text[::-1]},
        )
    ]

# Add to AppContext
class AppContext(BaseContext):
    def __init__(self, runner):
        super().__init__(runner)
        self.hello = self._bind(hello_world_policy)
        self.reverse = self._bind(reverse_policy)  # new

# Register with MCP
mcp.tool(reverse_policy)

# Optional REST endpoint
@app.get("/api/reverse")
async def reverse_api(text: str = Query(...)):
    msgs = await reverse_policy(text)
    return msgs[0].payload
```

---

# 8. License

MIT
