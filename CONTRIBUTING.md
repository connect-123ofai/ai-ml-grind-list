# Contributing

Full guidance — templates, the quality bar, how review works and how long it
takes — lives in **[section 7 of the README](README.md#7-how-to-contribute)**.
This file covers the mechanics.

## The one rule

**Never edit `README.md`.** It is generated from the files in `data/` and your
change will be overwritten on the next build. Edit the JSON, then run:

```bash
python3 scripts/generate_readme.py
```

No dependencies — the standard library is enough. Commit the regenerated
README alongside your data change; CI fails if the two disagree.

## Submitting a question

1. Copy the template that fits what you are submitting:
   - [`templates/Template_QnA.md`](templates/Template_QnA.md) — an interview question and its answer
   - [`templates/Template_Theory.md`](templates/Template_Theory.md) — a concept explainer
   - [`templates/Template_Coding.md`](templates/Template_Coding.md) — a problem with runnable code and tests
2. Fill it in without renaming any field. The keys map onto our ingestion
   contract, and a submission that parses cleanly reaches the live question
   bank without anyone re-typing it.
3. Open a pull request with **one question per PR**.

## Editing an existing list entry

Entries live in `data/grind-75-ml.json`, `data/grind-50-llm.json` and
`data/grind-more.json`.

```json
{
  "n": 12,
  "title": "Why would you use the Kernel Trick?",
  "type": "qna",
  "topic": "Classical Ml",
  "subtopic": "Supervised Learning",
  "level": "Medium",
  "minutes": 10,
  "minutes_max": null,
  "pro": false,
  "path": "/qnalab/theoryquestions/classical-ml/supervised-learning/why-would-you-use-the-kernel-trick"
}
```

| Field | Notes |
|---|---|
| `n` | Position in the list. Renumber the rest if you insert. |
| `type` | `qna` or `coding`. |
| `level` | `Easy`, `Medium` or `Hard`. |
| `minutes` | Time for a solid spoken answer, not for reading it. |
| `minutes_max` | Only when the budget is a range; otherwise `null`. |
| `pro` | Whether the worked answer sits behind 123ofAI Pro. |
| `path` | Site-relative. No domain, no UTM — the generator adds both. |

## Before you open a PR

1. `python3 scripts/generate_readme.py` and commit the result.
2. `python3 scripts/generate_readme.py --check` passes.
3. If you changed a `path`, load it and confirm the page resolves.
