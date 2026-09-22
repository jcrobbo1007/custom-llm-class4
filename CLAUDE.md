# CLAUDE.md — Class 4: Custom LLM (nanoGPT)

Persistent rules for any agent working in this repo. From the Class 4 handoff, section B.

## Mission

Two executed experiments of the class notebook + the fixed 48-case evals before/after each
+ a working chat interface + a README that explains learning from the actual saved numbers.
One public GitHub repo. README is the grading entry point.

**Status: both experiments are complete.** Do not re-run them casually — the committed
`results/` folders and executed notebooks are the evidence.

## Hard rules

1. **Ask before choosing.** Training steps, learning rate, extension categories and the
   prediction are Jack's. Brief him, wait, then act.
2. **Edit only section 1 of the notebook** (`CORPUS`, `TRAINING_STEPS`, `LEARNING_RATE`,
   `CORPUS_FOLDER`). Nothing else: not the split, seed, eval panels, sampling settings,
   temperature set, or model config. Any other change must be deliberate, asked for, declared.
3. **The exam stays outside the textbook.** Nothing from `evals/` — prompts, prefixes,
   choices, answer keys, explanations, eval outputs, chat transcripts, this file, the eval
   README — ever goes into `corpus/`, into a generated sentence, or into vocabulary building.
   `CORPUS_FOLDER` points only at `corpus/`. Inspect `eval_separation.json` after every run
   and run `scripts/leakage_check.py`. The exact-match checks do not catch paraphrases; you
   must. **The assignment states that leaked eval material can incur a substantial penalty to
   the overall grade, not only to the 3-point evaluation category.**
4. **Every number in the README comes from a saved file** in `results/`. No recalled,
   rounded-from-memory, or plausible numbers. If it can't be traced to a file, it's out.
5. **Fresh model per experiment.** Experiment 2 trains from scratch. Never fine-tune
   experiment 1's weights. Keep experiment 1's run folder intact.
6. **Report honestly.** A flat score, 0/24 on extension cases, unknown-word cases, or an
   extension that doesn't help are all valid findings. No silent re-runs. If a run is
   interrupted, say so and report completed steps.
7. **Notebook outputs stay.** The committed `.ipynb` files must show inspections, losses,
   samples, plots and eval cells inline. Never clear outputs.
8. **Chat replies come from the trained model.** No canned text, no other API. The transcript
   must be real and include a failure.
9. **Don't publish anything Jack lacks permission to share.** The extension corpus is text we
   wrote; fine to commit.

## Environment

Python 3.11–3.13 venv at `.venv`; kernel `llm313`. CPU is sufficient — 3,000 steps took
~34 seconds. `pip install -r requirements.txt jupyter nbconvert ipykernel`.

```bash
.venv/bin/jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.timeout=-1 --ExecutePreprocessor.kernel_name=llm313 \
  --output custom_llm.executed.expN.ipynb custom_llm.ipynb
```

Section 10 (chat) is an edit-prompt-and-rerun cell; under nbconvert it runs once with the
default prompt. Use `chat.py` for the transcript.

## Known gotchas

- `run_evals.py --output DIR` writes four files; `chat.py --transcript` refuses to overwrite.
- Eval result JSON uses keys `expected`, `predicted_choice`, `status`, `score`,
  `choice_probabilities`, `generated_text` — not `answer`/`correct`/`continuation`.
- `status` is `scored` or `out_of_vocabulary`; unscorable cases count as 0 in the all-case rate.
- The 512 vocabulary cap never bound (133 and 398 training types), so `omitted_types` is empty
  in both runs. A missing word means it was never written, not that it lost a frequency contest.
- Token IDs are per-run: `customer` is ID 28 in exp 1 and ID 74 in exp 2.
