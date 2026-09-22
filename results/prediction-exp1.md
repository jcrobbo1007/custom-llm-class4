# Prediction — written before experiment 1 trained

Author: Jack (jcrobbo1007). Recorded verbatim by Claude Code at the timestamp
below, before any training run with TRAINING_STEPS > 10 was started. Not edited
afterwards. The observations that test this prediction are in README.md.

Recorded: 2026-09-22 05:36:30 UTC

---

Experiment 1: training-panel loss will fall from roughly 4.9 (about ln of the vocab size) to below 1.0 by 1,500 steps and flatten; validation-panel loss will track it within about 0.05 because held-out passages share templates with training. Untrained samples will be random word soup; final samples will be grammatical starter-style sentences that sound plausible but repeat corpus templates. Evals: most of the 16 starter-pattern cases will pass (I expect 13–16), the 8 transfer cases will be mixed (3–5), and all 24 extension cases will be unscorable because the words are not in the vocabulary, so the all-case score will be near 16–20 out of 48.

Experiment 2: the added opposites and negation text will bring most of those six cases into vocabulary. I expect at least 2 of 3 opposites cases to score correctly because the pattern is a single-sentence association. I expect negation cases to become scorable but mostly fail: the model will favour the most recent or most frequent noun rather than the corrected one. The other 18 extension cases stay unscorable. Validation loss will be slightly higher than in experiment 1 because the corpus is more varied. Free continuations for negation prompts will be fluent but will not respect the "did not" correction.
