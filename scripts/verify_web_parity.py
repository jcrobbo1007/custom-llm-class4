#!/usr/bin/env python3
"""Prove the web interface and the terminal interface produce identical replies.

serve.py imports generate_reply/load_model from run_evals.py, which is the same
module chat.py imports. This script replays every turn in the web transcript
through that function directly and asserts the reply, unknown-word list and
truncation flag all match what the browser received.

    python scripts/verify_web_parity.py
Exit code 0 = identical, 1 = a mismatch.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run_evals import generate_reply, load_model, model_hash  # noqa: E402

TRANSCRIPT = Path("chat/web_chat_transcript.json")


def main():
    record = json.loads(TRANSCRIPT.read_text())
    model, vocabulary, _ = load_model(record["model"])

    digest = model_hash(model)
    print(f"Transcript model : {record['model']}")
    print(f"Transcript SHA   : {record['model_sha256']}")
    print(f"Loaded SHA       : {digest}")
    if digest != record["model_sha256"]:
        print("\nRESULT: FAIL - the transcript was produced by different weights.")
        return 1
    print("Model hash matches.\n")

    ok = True
    for i, turn in enumerate(record["turns"], 1):
        got = generate_reply(model, vocabulary, turn["prompt"],
                             seed=turn["seed"], temperature=turn["temperature"])
        same = (got["response"] == turn["reply"]
                and got["unknown_prompt_words"] == turn["unknown_words"]
                and got["prompt_truncated"] == turn["truncated"])
        ok &= same
        print(f"[{i}] seed={turn['seed']} T={turn['temperature']} "
              f"{'MATCH' if same else 'MISMATCH'}")
        print(f"    prompt : {turn['prompt'][:72]}")
        print(f"    web    : {turn['reply']!r}")
        if not same:
            print(f"    direct : {got['response']!r}")

    print("\nRESULT:", "PASS - web replies are identical to the chat.py code path."
          if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
