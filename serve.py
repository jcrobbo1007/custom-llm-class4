"""Web chat interface for the trained nanoGPT.

Serves the embedding viewer (with a chat panel) and a /chat endpoint on
localhost:4321. Generation is NOT reimplemented here: load_model, generate_reply
and model_hash are imported from run_evals.py, which is the same code path
chat.py uses, so the terminal and web interfaces produce identical replies for
the same prompt, temperature and seed.

No external API is called. No retraining happens. Nothing is written to corpus/.
Each request is an independent, fresh 48-token context.

    pip install -r requirements.txt
    python serve.py
    open http://localhost:4321
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field

from run_evals import generate_reply, load_model, model_hash

ROOT = Path(__file__).parent
DEFAULT_MODEL = ROOT / "results" / "exp2-extended" / "model.pt"
DEFAULT_CHECKPOINT = ROOT / "results" / "exp2-extended" / "checkpoint.json"
VIEWER = ROOT / "embedding-viewer.html"
TRANSCRIPT = ROOT / "chat" / "web_chat_transcript.json"
BASE_SEED = 2026
ALLOWED_TEMPERATURES = (0.3, 0.8, 1.2)

app = FastAPI(title="nanoGPT web chat", docs_url=None, redoc_url=None)
STATE = {}


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    temperature: float = 0.8
    seed: int | None = None


@app.get("/")
def index():
    return FileResponse(VIEWER)


@app.get("/checkpoint.json")
def checkpoint():
    """Only this one result file is exposed; the repo is not served as a directory."""
    return FileResponse(STATE["checkpoint"], media_type="application/json")


@app.get("/favicon.ico")
def favicon():
    """No icon; answer cleanly so the browser console stays free of 404s."""
    return Response(status_code=204)


@app.get("/meta")
def meta():
    return {"model": str(STATE["model_path"].relative_to(ROOT)),
            "model_sha256": STATE["model_sha256"],
            "completed_steps": STATE["saved"].get("completed_steps"),
            "vocabulary_size": len(STATE["vocabulary"]),
            "block_size": STATE["model"].config.block_size,
            "temperatures": list(ALLOWED_TEMPERATURES),
            "fresh_context_per_prompt": True}


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Empty prompt.")
    if not (0 < req.temperature <= 2):
        raise HTTPException(status_code=400, detail="Temperature must be in (0, 2].")

    seed = req.seed if req.seed is not None else BASE_SEED + len(STATE["turns"])
    result = generate_reply(STATE["model"], STATE["vocabulary"], req.prompt,
                            seed=seed, temperature=req.temperature)

    payload = {"reply": result["response"],
               "unknown_words": result["unknown_prompt_words"],
               "truncated": result["prompt_truncated"],
               "model_sha256": STATE["model_sha256"],
               "seed": seed,
               "temperature": req.temperature}

    STATE["turns"].append({"prompt": req.prompt, **payload,
                           "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    save_transcript()
    return JSONResponse(payload)


def save_transcript():
    TRANSCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT.write_text(json.dumps({
        "interface": "web (serve.py) - same model and generation code as chat.py",
        "model": str(STATE["model_path"].relative_to(ROOT)),
        "model_sha256": STATE["model_sha256"],
        "completed_steps": STATE["saved"].get("completed_steps"),
        "fresh_context_per_prompt": True,
        "block_size": STATE["model"].config.block_size,
        "max_tokens": 24,
        "external_api_used": False,
        "turns": STATE["turns"],
    }, indent=2) + "\n")


def boot(model_path: Path, checkpoint_path: Path):
    model, vocabulary, saved = load_model(model_path)
    STATE.update(model=model, vocabulary=vocabulary, saved=saved,
                 model_path=model_path, checkpoint=checkpoint_path,
                 model_sha256=model_hash(model), turns=[])
    return STATE


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    ap.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=4321)
    args = ap.parse_args()

    boot(args.model, args.checkpoint)
    print(f"Model      : {args.model}")
    print(f"SHA-256    : {STATE['model_sha256']}")
    print(f"Steps      : {STATE['saved'].get('completed_steps')}  |  vocab {len(STATE['vocabulary'])}")
    print(f"Open       : http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
