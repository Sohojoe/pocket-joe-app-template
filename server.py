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
