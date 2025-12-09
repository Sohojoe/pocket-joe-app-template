# Pocket Joe App Template

A minimal template for building **MCP tools**, **FastAPI endpoints**, and a **frontend UI** — all in one repo, deployable to **Railway** in a single deployment.

This template includes:
- MCP tool: **hello_world_policy**
- FastAPI endpoint: `/api/hello`
- MCP endpoint: `/mcp`
- Frontend: Single textbox → calls API → shows response
- **Single deployment**: Backend and frontend served from Railway

## Project Structure

```
pocket-joe-app-template/
├── server.py              # MCP + FastAPI backend (serves frontend)
├── pyproject.toml         # Python dependencies
├── nixpacks.toml          # Railway build configuration
├── railway.json           # Railway deployment settings
├── .gitignore
├── .vscode/
│   └── launch.json        # VSCode debug configuration
└── frontend/              # Vite/React/Tailwind UI
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── postcss.config.js
    ├── tailwind.config.js
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts
        └── index.css
```

## Local Development

### Backend

```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn server:app --reload --port 8000
```

**Test the backend:**
- `http://localhost:8000/api` → API info
- `http://localhost:8000/api/hello` → `{"greeting": "hello world"}`
- `http://localhost:8000/api/hello?text=joe` → `{"greeting": "hello joe"}`
- `http://localhost:8000/health` → `{"status": "ok"}`
- `http://localhost:8000/mcp` → MCP endpoint

**Note:** In local development, the backend runs on port 8000 but doesn't serve the frontend. Use the separate Vite dev server (below) for frontend development.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Opens at `http://localhost:5173`

### VSCode Debugging

Press `F5` or use the Run and Debug panel to start the FastAPI server with breakpoints enabled.

## Deployment to Railway

This template is configured for **single-deployment** to Railway. The build process automatically:
1. Installs Node.js and Python dependencies
2. Builds the frontend (`npm run build`)
3. Starts FastAPI server which serves both the API and frontend

### Deploy Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click **New Project** → **Deploy from GitHub repo**
   - Select your repository
   - Railway auto-detects the configuration via `nixpacks.toml`
   - Wait ~3-5 minutes for build (includes frontend build)

3. **Generate Public Domain**
   - Click on your deployed service in the Railway dashboard
   - Go to **Settings** tab
   - Find **Networking** → **Public Networking** section
   - Click **Generate Domain**
   - Railway will generate a public URL (e.g., `https://your-app.up.railway.app`)

4. **Access Your App**
   - Use the generated Railway URL to access your app
   - Frontend: `https://your-app.up.railway.app/`
   - API: `https://your-app.up.railway.app/api/hello`
   - MCP: `https://your-app.up.railway.app/mcp`

### How It Works

The `nixpacks.toml` file configures Railway to:
- Install both Node.js 20 and Python 3.12
- Run `npm install` in the frontend directory
- Build the frontend with `npm run build` → creates `frontend/dist/`
- Start the FastAPI server, which serves:
  - API endpoints at `/api/*`
  - MCP endpoint at `/mcp`
  - Static frontend files from `frontend/dist/` at `/`

### Automatic Redeployment

Push changes to GitHub and Railway auto-deploys:
```bash
git add .
git commit -m "Update feature"
git push
```

Railway rebuilds frontend and restarts the server automatically.

## Use MCP in Claude Desktop

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

## Adding More Tools

1. Create your policy function with `@policy.tool` decorator in `server.py`
2. Add to `AppContext` with `self._bind(YourPolicy)`
3. Register with FastMCP: `mcp.tool(your_policy)`
4. Optionally add a REST endpoint in FastAPI
5. Push to GitHub — Railway auto-deploys

### Example: Adding a Reverse Tool

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
    result = await ctx.reverse(text=text)
    return result[0].payload
```

## Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server implementation
- [Pocket Joe](https://github.com/PocketJoeAI/pocket-joe) - Policy-based workflows
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

**Frontend:**
- [Vite](https://vite.dev/) - Build tool
- [React](https://react.dev/) - UI framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Tailwind CSS](https://tailwindcss.com/) - Styling

## License

MIT
