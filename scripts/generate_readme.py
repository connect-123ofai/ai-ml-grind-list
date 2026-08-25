#!/usr/bin/env python3
"""
Build README.md from the JSON files in data/.

The lists are the product, so they live in structured data and the README is
derived from it. Editing the README by hand will be overwritten; edit the JSON.

Standard library only, so `python3 scripts/generate_readme.py` works on a clean
checkout with no install step.

Usage:
    python3 scripts/generate_readme.py           # write README.md
    python3 scripts/generate_readme.py --check   # exit 1 if README is stale
"""

import argparse
import json
import pathlib
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
README = ROOT / "README.md"

SITE = "https://123ofai.com"
UTM_SOURCE = "github"
UTM_MEDIUM = "repo"

# Order matters: this is the order the lists appear in the README.
LISTS = ["grind-75-ml.json", "grind-50-llm.json"]


def question_url(path: str, campaign: str) -> str:
    """Absolute, UTM-tagged, and safe to drop inside a Markdown link.

    Slugs may contain parentheses (e.g. `...-(2-layer-ann)`), which terminate a
    Markdown link target early and silently produce a broken link. Percent-encode
    them; `quote` leaves the rest of the path alone.
    """
    safe = quote(path, safe="/-_.~")
    return (
        f"{SITE}{safe}"
        f"?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}&utm_campaign={campaign}"
    )


def md_cell(text: str) -> str:
    """Escape what would otherwise break out of a table cell."""
    return text.replace("|", "\\|").replace("\n", " ").strip()


def fmt_time(q):
    """Most entries are a single figure; a couple are budgeted as a range."""
    lo, hi = q.get("minutes"), q.get("minutes_max")
    if not lo:
        return None
    return f"{lo}\u2013{hi}m" if hi else f"{lo}m"


def fmt_hours(minutes: int) -> str:
    hours = minutes / 60
    return f"{hours:.1f}".rstrip("0").rstrip(".") + "h"


def render_list(meta: dict) -> str:
    campaign = meta["slug"].replace("-", "_")
    qs = meta["questions"]
    free = sum(1 for q in qs if not q["pro"])
    coding = sum(1 for q in qs if q["type"] == "coding")

    out = []
    out.append(f'## {meta["name"]}')
    out.append("")
    out.append(meta["description"])
    out.append("")
    d = meta.get("difficulty", {})
    spread = " · ".join(
        f'{d[k]} {k.lower()}' for k in ("Easy", "Medium", "Hard") if d.get(k)
    )
    out.append(
        f'**{len(qs)} questions** · **{fmt_hours(meta["total_minutes"])}** of focused practice · '
        f"{coding} hands-on coding · {free} open access"
    )
    out.append("")
    out.append(f"Difficulty: {spread}")
    out.append("")
    out.append(f'[Solve this list on 123ofAI →]({meta["platform_url"]}'
               f"?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}&utm_campaign={campaign})")
    out.append("")
    # A task list, not a table: GitHub only renders tickable checkboxes in
    # list items, and progress-tracking on a fork is the whole point of a
    # grind list. Metadata rides inline instead of in columns.
    for q in qs:
        url = question_url(q["path"], campaign)
        title = md_cell(q["title"])
        bits = []
        if q.get("level"):
            bits.append(f'`{q["level"]}`')
        bits.append(f'*{md_cell(q["subtopic"])}*')
        if q["type"] == "coding":
            bits.append("`code`")
        t = fmt_time(q)
        if t:
            bits.append(t)
        if q["pro"]:
            bits.append("🔒")
        out.append(f'- [ ] **{q["n"]}.** [{title}]({url}) · ' + " · ".join(bits))
    out.append("")

    # Topic index — the flat list is the practice order; this is for browsing.
    by_topic = {}
    for q in qs:
        by_topic.setdefault(q["subtopic"], []).append(q)
    out.append("<details>")
    out.append(f'<summary><b>{meta["name"]} grouped by area</b> '
               f"({len(by_topic)} areas)</summary>")
    out.append("")
    for topic in sorted(by_topic, key=lambda t: (-len(by_topic[t]), t)):
        items = by_topic[topic]
        nums = ", ".join(f'[{q["n"]}]({question_url(q["path"], campaign)})' for q in items)
        out.append(f"- **{md_cell(topic)}** ({len(items)}) — {nums}")
    out.append("")
    out.append("</details>")
    out.append("")
    return "\n".join(out)


def build() -> str:
    metas = [json.loads((DATA / f).read_text(encoding="utf-8")) for f in LISTS]
    total_q = sum(m["count"] for m in metas)
    total_min = sum(m["total_minutes"] for m in metas)

    p = []
    p.append("# Grind ML — curated ML & LLM interview question lists")
    p.append("")
    p.append(
        "Two ordered, finite lists for machine learning and LLM interview prep. "
        f"**{total_q} questions**, roughly **{fmt_hours(total_min)}** of focused work — "
        "not a link dump of everything that exists."
    )
    p.append("")
    p.append(
        "The full lists are below. Read them here, tick them off here, or fork the "
        "repo and track your own progress. Each question links through to 123ofAI "
        "where you can actually answer it and get feedback."
    )
    p.append("")
    p.append("## The lists")
    p.append("")
    p.append("| List | Questions | Time | Easy / Medium / Hard | Focus |")
    p.append("|---|---|---|---|---|")
    for m in metas:
        d = m.get("difficulty", {})
        mix = f'{d.get("Easy", 0)} / {d.get("Medium", 0)} / {d.get("Hard", 0)}'
        p.append(
            f'| [{m["name"]}](#{m["slug"]}) | {m["count"]} | '
            f'{fmt_hours(m["total_minutes"])} | {mix} | {md_cell(m["description"])} |'
        )
    p.append("")
    p.append("## How to use this")
    p.append("")
    p.append("1. **Fork the repo** — then tick checkboxes in your own copy as you go.")
    p.append("2. **Work in order.** The lists are sequenced, not sorted by difficulty — "
             "each is tagged `Easy` / `Medium` / `Hard` so you can trade breadth for "
             "depth when time is short.")
    p.append("3. **Time-box.** The estimate next to each question is roughly what a "
             "solid spoken answer takes. If you're well over, that's the gap to study.")
    p.append("4. **Click through to answer.** Reading a question and *thinking* you "
             "could answer it is the classic prep trap.")
    p.append("")
    p.append("🔒 marks questions whose full worked solution is part of 123ofAI Pro. "
             "Every question itself is listed here in full.")
    p.append("")
    p.append("---")
    p.append("")
    for m in metas:
        p.append(render_list(m))
        p.append("---")
        p.append("")
    p.append("## Contributing")
    p.append("")
    p.append("Corrections, better phrasings and new questions are welcome — see "
             "[CONTRIBUTING.md](CONTRIBUTING.md). Edit the JSON in `data/`, never "
             "`README.md`; the README is generated.")
    p.append("")
    p.append("```bash")
    p.append("python3 scripts/generate_readme.py")
    p.append("```")
    p.append("")
    p.append("## About")
    p.append("")
    p.append(
        f"Maintained by [123ofAI]({SITE}?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}"
        "&utm_campaign=about), an AI/ML interview preparation platform. "
        "Questions, mock interviews, ML system design and verified engineering case studies."
    )
    p.append("")
    p.append("Licensed [CC BY 4.0](LICENSE) — use the lists anywhere, with attribution.")
    p.append("")
    return "\n".join(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if README.md is out of date")
    args = ap.parse_args()

    content = build()
    if args.check:
        current = README.read_text(encoding="utf-8") if README.exists() else ""
        if current != content:
            print("README.md is stale — run: python3 scripts/generate_readme.py",
                  file=sys.stderr)
            return 1
        print("README.md is up to date.")
        return 0

    README.write_text(content, encoding="utf-8")
    print(f"Wrote {README.relative_to(ROOT)} "
          f"({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
