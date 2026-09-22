# MORNING.md — what ran overnight, and what is left for Jack

Everything finished in one attended session. Training was far faster than the handoff
assumed, so there was no unattended overnight phase.

## The four eval numbers

| Experiment / stage | Correct / 48 | Scorable / 48 | Accuracy among scorable | Coverage |
| --- | --- | --- | --- | --- |
| Starter, untrained | 9 | 24 | 37.50% | 50.0% |
| Starter, trained | **20** | 24 | 83.33% | 50.0% |
| Expanded, untrained | 3 | 29 | 10.34% | 60.4% |
| Expanded, trained | **24** | 29 | 82.76% | 60.4% |

The headline improvement (20 → 24) did **not** come from the categories we targeted. All five
newly-scorable extension cases scored 0. The +4 came from `new_wording` (4/8 → 8/8), a side
effect nobody predicted. README explains this at length; it is the most interesting result in
the repo, not a problem to fix.

## What ran

- 10-step setup check (0.416 s) — timing only, run folder deleted, kept at
  `results/setup-10-steps/` and explicitly labelled not-evidence.
- Experiment 1, starter corpus, 3,000 steps / lr 0.001 — 33.478 s, not interrupted.
- Experiment 2, starter + `corpus/extension/`, same settings, trained from scratch — 35.552 s,
  not interrupted.
- `scripts/leakage_check.py` over `corpus/extension/` — **PASS**, worst overlap 6 tokens.
- Chat transcript via piped `chat.py` — 6 real turns, 3 of them failures.
- `run_evals.py` rerun against the committed `model.pt` — reproduces 24/48, 29 scorable.
- README written from the saved files; three numbers spot-checked against their sources.

## What failed or is missing

1. **The repo was not created or pushed.** This session's GitHub credential returns
   403 `Resource not accessible by integration` on repository creation, and its scope covers
   only `networking-tracker`. The work is committed locally but is **not on GitHub yet**.
   You must create the empty public repo `custom-llm-class4` yourself, then it can be pushed.
2. **`HANDOFF.md` was not reproduced into the repo.** `CLAUDE.md` (section B of the handoff)
   was written and committed; the full handoff document was not, since it is planning
   scaffolding rather than a graded artifact. Add it yourself if you want it in the repo.
3. **Chat visual: done, with a caveat.** `chat/chat-terminal.png` is committed — a rendering
   of `chat/chat-session.txt`, the raw capture of a real terminal session run in the container.
   It is honestly labelled in the image footer and in the README as a rendering, **not** a
   photograph of a screen. If you prefer a true screen capture from your own machine, take one
   and add it as `chat/chat-screenshot.png`; nothing else needs to change.
4. **Embedding-viewer screenshot: done.** `results/viewer.png` shows the viewer with exp 3's
   `checkpoint.json` loaded, inspecting `quiet`. Its nearest vectors are `green` 0.692,
   `noisy` 0.682, `hot` 0.678 — the opposites failure visible directly in the weights.

## Added after submission

5. **Experiment 3 — depth (`n_layer` 2→4).** Run as a follow-up to the README's proposed next
   experiment, on a separate notebook copy so `custom_llm.ipynb` stays byte-identical to
   upstream. Result: 25/48 (up from 24), opposites 1/3 (up from 0/3), negation still 0/3.
   Partially confirms the hypothesis. Full write-up in the README addendum; experiments 1 and
   2 were not touched.

## What Jack still has to do

1. **Create the repo** — github.com/new, owner `jcrobbo1007`, name `custom-llm-class4`,
   **public**, no README/gitignore/license. Then the local commits can be pushed.
2. **Optional — a true screen capture from your own machine.** The rendered terminal image
   already satisfies the "screenshot or short recording" requirement, so this is belt-and-braces:
   ```bash
   .venv\Scripts\pip install torch
   .venv\Scripts\python chat.py --model results\exp2-extended\model.pt --transcript chat\live.json
   ```
   Try `the opposite of tall is` — it answers `river .`, which is the failure the README
   leans on. Save as `chat/chat-screenshot.png` and add `![Chat screenshot](chat/chat-screenshot.png)`
   under the Chat interface heading.
3. **Eyeball the corpus for leakage.** Open `corpus/extension/opposites.md` and
   `corpus/extension/negation.md` and confirm no line looks like a test story. The two closest
   lines are `negation.md:26` (`the scarf is not grey . it is blue . the scarf is blue .`) and
   `negation.md:34` (`the shed is not empty . it is closed . the shed is closed .`) — both use
   different nouns and different negated attributes from the eval items. Full per-case report:
   `results/exp2-extended/leakage_check.txt`.
4. **Open the repo signed out** and confirm both executed notebooks render with outputs, the
   SVG shows, and the result links resolve.
5. **Submit** the URL via bCourses / the submissions portal.
