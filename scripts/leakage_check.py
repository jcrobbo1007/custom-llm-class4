#!/usr/bin/env python3
"""Check that no eval item leaked into the training corpus.

The notebook's own check rejects EXACT reserved prefixes. This is stricter and
covers the material we wrote by hand in corpus/extension/:

  1. No eval prompt appears as a contiguous token substring of any corpus line.
  2. No corpus line shares a contiguous run of >= MAX_NGRAM tokens with any prompt.
  3. No corpus line reproduces an answer-choice list.
  4. Reports the WORST overlap found for every one of the 48 cases, so a clean
     result is verifiable rather than merely asserted.

Usage:  python scripts/leakage_check.py [--corpus corpus/extension] [--max-ngram 7]
Exit code 0 = clean, 1 = leakage found.
"""
import argparse, json, re, sys
from pathlib import Path

MAX_NGRAM_DEFAULT = 7

def tokens(text):
    """Same tokenisation the notebook uses, so comparison is like-for-like."""
    return re.findall(r"\w+(?:['’]\w+)*|[^\w\s]", text.lower(), flags=re.UNICODE)

def ngrams(seq, n):
    return {tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)} if len(seq) >= n else set()

def longest_common_run(a, b):
    """Length of the longest contiguous token run shared by a and b."""
    if not a or not b:
        return 0
    best = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus/extension")
    ap.add_argument("--evals", default="evals/language_evals.json")
    ap.add_argument("--max-ngram", type=int, default=MAX_NGRAM_DEFAULT)
    args = ap.parse_args()

    data = json.loads(Path(args.evals).read_text())
    cases = data["cases"] if isinstance(data, dict) and "cases" in data else data

    corpus_files = sorted(Path(args.corpus).rglob("*.md")) + sorted(Path(args.corpus).rglob("*.txt"))
    if not corpus_files:
        print(f"No corpus files under {args.corpus}", file=sys.stderr)
        return 1

    lines = []  # (path, lineno, raw, tokens)
    for path in corpus_files:
        for n, raw in enumerate(path.read_text().splitlines(), 1):
            if raw.strip():
                lines.append((path, n, raw.strip(), tokens(raw)))

    print(f"Corpus files checked : {len(corpus_files)}")
    for p in corpus_files:
        print(f"  {p}")
    print(f"Non-empty lines      : {len(lines)}")
    print(f"Eval cases           : {len(cases)}")
    print(f"Max allowed shared contiguous run : {args.max_ngram - 1} tokens "
          f"(a run of {args.max_ngram}+ fails)")
    print()

    failures = []
    report = []

    for case in cases:
        prompt_tok = tokens(case["prompt"])
        worst_len, worst_at = 0, None

        for path, n, raw, line_tok in lines:
            # 1. exact containment
            if len(prompt_tok) <= len(line_tok):
                joined_line = " ".join(line_tok)
                if " ".join(prompt_tok) in joined_line:
                    failures.append(
                        f"EXACT PROMPT in {path}:{n} -> case {case['id']}\n    line: {raw}")

            run = longest_common_run(prompt_tok, line_tok)
            if run > worst_len:
                worst_len, worst_at = run, (path, n, raw)

        if worst_len >= args.max_ngram:
            path, n, raw = worst_at
            failures.append(
                f"{worst_len}-TOKEN OVERLAP with case {case['id']} at {path}:{n}\n"
                f"    prompt: {case['prompt']}\n    line  : {raw}")

        report.append((case["id"], case.get("category", "?"), worst_len, worst_at))

    # 3. answer-choice lists reproduced verbatim
    for case in cases:
        choice_run = tokens(" ".join(case["choices"]))
        for path, n, raw, line_tok in lines:
            if len(choice_run) >= 3 and longest_common_run(choice_run, line_tok) >= len(choice_run):
                failures.append(f"CHOICE LIST reproduced in {path}:{n} -> case {case['id']}\n    line: {raw}")

    print("Worst contiguous overlap per case (tokens shared with the nearest corpus line):")
    print(f"{'case':10s} {'category':24s} {'worst':>5s}  nearest corpus line")
    for cid, cat, ln, at in sorted(report, key=lambda r: -r[2]):
        where = f"{at[0].name}:{at[1]}" if at else "-"
        snippet = (at[2][:64] + "...") if at and len(at[2]) > 64 else (at[2] if at else "")
        flag = "  <-- FAIL" if ln >= args.max_ngram else ""
        print(f"{cid:10s} {cat:24s} {ln:5d}  [{where}] {snippet}{flag}")
    print()

    if failures:
        print(f"LEAKAGE FOUND: {len(failures)} problem(s)\n")
        for f in failures:
            print("  " + f)
        print("\nRESULT: FAIL")
        return 1

    print("No eval prompt, prompt fragment of the forbidden length, or choice list "
          "appears in the training corpus.")
    print("NOTE: this is a lexical check. It cannot detect a paraphrase that reuses "
          "no long token run. The corpus was also written by hand to use different "
          "names, objects and framings from every eval case.")
    print("\nRESULT: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
