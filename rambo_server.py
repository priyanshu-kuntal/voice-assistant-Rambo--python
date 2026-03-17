import os
import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rambo_core import RamboCore


def get_token() -> str:
    # Set RAMBO_TOKEN in your environment for a stable token.
    # If not set, a random token is generated on each run and printed.
    tok = os.environ.get("RAMBO_TOKEN", "").strip()
    if tok:
        return tok
    return secrets.token_urlsafe(24)


TOKEN = get_token()
core = RamboCore()

app = FastAPI(title="RAMBO Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandIn(BaseModel):
    command: str


class CommandOut(BaseModel):
    ok: bool
    spoken: str


def require_token(x_rambo_token: str | None) -> None:
    if not x_rambo_token or x_rambo_token != TOKEN:
        raise HTTPException(status_code=401, detail="Missing/invalid token")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True}


@app.post("/command", response_model=CommandOut)
def command(body: CommandIn, x_rambo_token: str | None = Header(default=None)) -> CommandOut:
    require_token(x_rambo_token)
    res = core.handle_command(body.command)
    return CommandOut(ok=res.ok, spoken=res.spoken)


if __name__ == "__main__":
    print("RAMBO Server starting")
    print(f"Token: {TOKEN}")
    print("Run with: python -m uvicorn rambo_server:app --host 0.0.0.0 --port 8787")

