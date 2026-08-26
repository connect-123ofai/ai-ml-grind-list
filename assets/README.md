# Screenshots

`scripts/generate_readme.py` embeds each image **only if the file exists**, so a
missing screenshot renders as an absent image rather than a broken one. Drop the
files in here with these exact names and re-run the generator.

| Filename | What to capture | Suggested page |
|---|---|---|
| `design-studio.png` | A design mid-build on the canvas — several blocks placed and connected, ideally with the evaluation panel showing segment scores. | `/qnalab/system-design/design/<slug>` |
| `coding-platform.png` | The editor with a real problem open and a passing test run visible. | `/qnalab/mlcodingproblems/<slug>` |
| `interview-report.png` | A marked answer — the report showing what was covered and what was missed. | any question, after submitting an answer |

Guidance:

- **Light mode, 1600px wide or more.** GitHub renders READMEs on a light
  background by default; a dark screenshot on a light page reads as a mistake.
- **Real content, not lorem.** A screenshot with placeholder text undoes the
  point of showing the product.
- **No personal data.** Check the header, avatar and any email address before
  capturing — this repo will be public.
- **PNG, under ~500 KB each.** They are inlined on the README, which is the
  first thing a visitor loads.
