# Contributing

Thanks for helping improve these lists.

## The one rule

**Never edit `README.md`.** It is generated from the files in `data/` and your
change will be overwritten on the next build. Edit the JSON, then run:

```bash
python3 scripts/generate_readme.py
```

No dependencies — the standard library is enough.

## What's welcome

- **Corrections** — a question that is worded ambiguously, has a typo, or is
  technically wrong. These are the most valuable contributions.
- **Better time estimates** — if a question consistently takes far longer than
  the estimate, say so.
- **New questions** — see the bar below.
- **Ordering** — if a question clearly belongs earlier or later in the sequence.

## The bar for a new question

A question earns a place only if it is asked in real interviews and isn't
already covered. Lists that grow without limit stop being useful; the point of
a grind list is that it *ends*. Adding one usually means arguing which one it
replaces.

## Question format

```json
{
  "n": 12,
  "title": "Why would you use the Kernel Trick?",
  "type": "qna",
  "topic": "Classical ML",
  "subtopic": "Supervised Learning",
  "minutes": 10,
  "level": null,
  "pro": false,
  "path": "/qnalab/theoryquestions/classical-ml/supervised-learning/why-would-you-use-the-kernel-trick"
}
```

| Field | Notes |
|---|---|
| `n` | Position in the list. Renumber the rest if you insert. |
| `type` | `qna` or `coding`. |
| `minutes` | Time for a solid spoken answer, not for reading it. |
| `pro` | Whether the worked solution sits behind 123ofAI Pro. |
| `path` | Site-relative. No domain, no UTM — the generator adds both. |

## Before you open a PR

1. Run the generator and commit the regenerated `README.md` alongside your
   data change.
2. Check `python3 scripts/generate_readme.py --check` passes.
3. If you changed a `path`, confirm the page actually loads.
