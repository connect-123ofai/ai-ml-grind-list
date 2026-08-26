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
import re
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
README = ROOT / "README.md"

SITE = "https://123ofai.com"
UTM_SOURCE = "github"
UTM_MEDIUM = "repo"
CONTACT_EMAIL = "contact@aspirefrontiers.com"

LISTS = ["grind-75-ml.json", "grind-75-llm.json"]
MORE = "grind-more.json"

# One palette, used for every badge and nothing else. Indigo carries the brand,
# violet the secondary metric, emerald the "this is free" promise.
INDIGO, VIOLET, EMERALD, SLATE, PINK = "6366F1", "8B5CF6", "10B981", "64748B", "EC4899"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def anchor(heading: str) -> str:
    """GitHub's heading-anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    a = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s+", "-", a)


def badge(label: str, value: str, colour: str) -> str:
    def esc(s):
        return s.replace("-", "--").replace("_", "__").replace(" ", "%20")
    return (f"https://img.shields.io/badge/{esc(label)}-{esc(value)}-{colour}"
            "?style=flat-square")


def question_url(path: str, campaign: str) -> str:
    """Absolute, UTM-tagged, and safe to drop inside a Markdown link.

    Slugs may contain parentheses (e.g. `...-(2-layer-ann)`), which terminate a
    Markdown link target early and silently produce a broken link. Percent-encode
    them; `quote` leaves the rest of the path alone.
    """
    return (f"{SITE}{quote(path, safe='/-_.~')}"
            f"?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}&utm_campaign={campaign}")


def site_url(path: str, campaign: str) -> str:
    return f"{SITE}{path}?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}&utm_campaign={campaign}"


def md_cell(text) -> str:
    """Escape what would otherwise break out of a table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def fmt_time(q) -> str:
    """Most entries are a single figure; a couple are budgeted as a range."""
    lo, hi = q.get("minutes"), q.get("minutes_max")
    if not lo:
        return ""
    return f"{lo}\u2013{hi}m" if hi else f"{lo}m"


def fmt_hours(minutes: int) -> str:
    return f"{minutes / 60:.1f}".rstrip("0").rstrip(".") + "h"


def question_line(q: dict, campaign: str) -> str:
    """One tickable row. A task list, not a table: GitHub only renders
    checkboxes in list items, and tracking progress on a fork is the whole
    point of a grind list."""
    bits = []
    if q.get("level"):
        bits.append(f'`{q["level"]}`')
    bits.append(f'*{md_cell(q["subtopic"])}*')
    if q.get("type") == "coding":
        bits.append("`code`")
    t = fmt_time(q)
    if t:
        bits.append(t)
    return (f'- [ ] **{q["n"]}.** [{md_cell(q["title"])}]'
            f'({question_url(q["path"], campaign)}) · ' + " · ".join(bits))


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------

def render_list_section(num: int, meta: dict) -> str:
    campaign = meta["slug"].replace("-", "_")
    qs, d = meta["questions"], meta.get("difficulty", {})
    coding = sum(1 for q in qs if q["type"] == "coding")

    by_sub: dict[str, list] = {}
    for q in qs:
        by_sub.setdefault(q["subtopic"], []).append(q)

    o = [f'## {num}. {meta["name"]}', ""]
    o.append(f'> {meta["description"]}')
    o.append("")
    o.append(
        f'<img src="{badge("Questions", str(len(qs)), INDIGO)}"> '
        f'<img src="{badge("Practice", fmt_hours(meta["total_minutes"]), VIOLET)}"> '
        f'<img src="{badge("Access", "all free", EMERALD)}"> '
        f'<img src="{badge("Areas", str(len(by_sub)), SLATE)}">'
    )
    o.append("")
    o.append(
        f'**{d.get("Easy",0)} easy · {d.get("Medium",0)} medium · {d.get("Hard",0)} hard**'
        + (f" · **{coding} hands-on coding**" if coding else "")
    )
    o.append("")
    o.append("<details open>")
    o.append(f"<summary><b>Sub-topics covered</b></summary>")
    o.append("")
    o.append("| Sub-topic | Qs | Jump to |")
    o.append("|:--|--:|:--|")
    for sub in sorted(by_sub, key=lambda s: (-len(by_sub[s]), s)):
        items = by_sub[sub]
        nums = " ".join(f'[`{q["n"]}`]({question_url(q["path"], campaign)})' for q in items[:14])
        if len(items) > 14:
            nums += f" *+{len(items)-14}*"
        o.append(f"| **{md_cell(sub)}** | {len(items)} | {nums} |")
    o.append("")
    o.append("</details>")
    o.append("")
    o.append("The list is sequenced — work top to bottom. Fork the repo to tick items off in your own copy.")
    o.append("")
    for q in qs:
        o.append(question_line(q, campaign))
    o.append("")
    o.append(f'<div align="right"><a href="{site_url("/qnalab/lists/" + meta["platform_key"], campaign)}"><b>Solve this list on 123ofAI →</b></a></div>')
    o.append("")
    return "\n".join(o)


def render_more_section(num: int, meta: dict) -> str:
    campaign = "grind_more"
    total_available = sum(g["available"] for g in meta["groups"])
    o = [f'## {num}. Grind More', ""]
    o.append(f'> {meta["description"]}')
    o.append("")
    o.append(
        f'<img src="{badge("Extra questions", str(meta["count"]), INDIGO)}"> '
        f'<img src="{badge("Areas", str(len(meta["groups"])), SLATE)}"> '
        f'<img src="{badge("In the wider bank", f"{total_available}+ free", EMERALD)}">'
    )
    o.append("")
    o.append("Done with both lists? These come from the same bank, grouped by area, and every one is free to attempt.")
    o.append("")
    for g in meta["groups"]:
        o.append("<details>")
        o.append(f'<summary><b>{md_cell(g["topic"])}</b> — {len(g["questions"])} shown of {g["available"]} free</summary>')
        o.append("")
        for q in g["questions"]:
            bits = []
            if q.get("level"):
                bits.append(f'`{q["level"]}`')
            bits.append(f'*{md_cell(q["subtopic"])}*')
            t = fmt_time(q)
            if t:
                bits.append(t)
            o.append(f'- [{md_cell(q["title"])}]({question_url(q["path"], campaign)}) · ' + " · ".join(bits))
        o.append("")
        o.append(f'[Browse all {g["available"]} {md_cell(g["topic"])} questions →]'
                 f'({site_url("/qnalab/theoryquestions/" + g["key"], campaign)})')
        o.append("")
        o.append("</details>")
        o.append("")
    return "\n".join(o)


def render_platform_section(num: int) -> str:
    """Screenshots render only if the file is actually present, so a missing
    asset is an absent image rather than a broken one."""
    campaign = "platform"
    shots = [
        ("design-studio.png", "ML Design Studio",
         "Drag real components onto a canvas — feature store, model registry, serving "
         "endpoint, monitoring — and have the design scored across six segments, from "
         "data pipeline to responsible AI.", "/qnalab/system-design"),
        ("coding-platform.png", "Coding Platform",
         "Write and run ML code in the browser against a real test suite. NumPy and "
         "Python, no local setup, immediate pass or fail.", "/qnalab/mlcodingproblems"),
        ("interview-report.png", "Test Your Understanding",
         "Answer in your own words and have it marked — what you covered, what you "
         "missed, and what an interviewer would have followed up on.", "/qnalab/generic"),
    ]
    o = [f"## {num}. Come Practice on the Platform", ""]
    o.append("> Reading a question and *thinking* you could answer it is the classic prep trap.")
    o.append("")
    o.append("Every question above links straight into the place you can find out whether that's true.")
    o.append("")
    for fname, title, blurb, path in shots:
        o.append(f"### {title}")
        o.append("")
        o.append(blurb)
        o.append("")
        if (ASSETS / fname).exists():
            o.append(f'<a href="{site_url(path, campaign)}">'
                     f'<img src="assets/{fname}" alt="{title}" width="100%"></a>')
            o.append("")
        o.append(f'[Try it →]({site_url(path, campaign)})')
        o.append("")
    return "\n".join(o)


def render_contributing_section(num: int) -> str:
    o = [f"## {num}. How to Contribute", ""]
    o.append("> These lists get better when the people who actually sat the interview say what was asked.")
    o.append("")
    o.append(f'<img src="{badge("PRs", "welcome", PINK)}"> '
             f'<img src="{badge("Review", "by the 123ofAI team", SLATE)}">')
    o.append("")
    o.append("### Pick a template")
    o.append("")
    o.append("| Submitting | Template | For |")
    o.append("|:--|:--|:--|")
    o.append("| An interview question and its answer | [`Template_QnA.md`](templates/Template_QnA.md) | The common case |")
    o.append("| A concept explainer, not a question | [`Template_Theory.md`](templates/Template_Theory.md) | Notes that teach an idea |")
    o.append("| A problem with runnable code and tests | [`Template_Coding.md`](templates/Template_Coding.md) | In-browser coding problems |")
    o.append("")
    o.append(
        "Every field maps one-to-one onto our question ingestion contract. That's "
        "deliberate: an approved submission loads straight into our ingestion form "
        "and reaches the live bank without anyone re-typing it. **Don't rename keys "
        "or leave required fields blank** — a submission that doesn't parse can't be "
        "loaded automatically and takes considerably longer to land."
    )
    o.append("")
    o.append("### The quality bar")
    o.append("")
    o.append("| | |")
    o.append("|:--|:--|")
    o.append("| **Real** | Asked in an actual interview, or a concept those interviews genuinely rely on. Not invented to pad a list. |")
    o.append("| **Not already covered** | Search the lists and the bank first. A rephrasing of an existing question is a duplicate. |")
    o.append("| **Discriminating** | It should separate someone who understands the idea from someone who memorised the definition. |")
    o.append("| **Answerable in the stated time** | If your own answer runs past `time_minutes`, the estimate or the scope is wrong. |")
    o.append("| **Sourced** | Say where it came from. No stated source is declined — we won't publish what we can't stand behind. |")
    o.append("| **Yours to give** | No copyrighted material from books, paid courses or another site. |")
    o.append("")
    o.append("The bar rises as the lists fill up. Once an area is well covered, a new question usually has to *replace* one rather than join it — say which, and why yours is better.")
    o.append("")
    o.append("### How your PR gets reviewed")
    o.append("")
    o.append(
        "Every submission is read by someone on the 123ofAI team — the same people who "
        "maintain the question bank. We check it against the bar above, verify the "
        "technical content, and edit for clarity where that helps. Expect comments "
        "rather than a silent close: if we ask for changes, it's because we intend to "
        "merge it once they land."
    )
    o.append("")
    o.append("Outcomes are one of three — **merged**, **changes requested**, or **declined with a reason**. We don't close submissions without saying why.")
    o.append("")
    o.append("### How long it takes")
    o.append("")
    o.append(
        "Review is manual, done by a small team alongside the rest of their work. "
        "**Please be patient** — a considered review of a technical question takes "
        "longer than a rubber stamp, and that's the point."
    )
    o.append("")
    o.append(f"If something genuinely needs to move faster — a factual error on a live question, a hiring deadline — email **{CONTACT_EMAIL}** with the PR link and we'll pull it forward.")
    o.append("")
    o.append("<details>")
    o.append("<summary><b>A few practical things</b></summary>")
    o.append("")
    o.append("- **One question per pull request.** Batched submissions get reviewed at the speed of their weakest entry.")
    o.append("- **Never edit `README.md`.** It's generated from `data/`. Run `python3 scripts/generate_readme.py` and commit the result.")
    o.append("- **Corrections don't need a template.** A typo or wrong claim can just be a PR with the fix and a one-line explanation.")
    o.append("- **Not sure it qualifies?** Open an issue and ask before writing it up.")
    o.append("- **Anonymity is fine.** `company_tag` can be blank; we'll never publish an employer you didn't name yourself.")
    o.append("")
    o.append("</details>")
    o.append("")
    return "\n".join(o)


def render_contributors_section(num: int) -> str:
    o = [f"## {num}. Contributors Wall", ""]
    o.append("> Everyone here has had a question, a correction or an improvement merged. Not ordered by volume — a single sharp correction counts.")
    o.append("")
    o.append("<!-- CONTRIBUTORS:START — add a row per merged contribution. -->")
    o.append("")
    o.append("| Contributor | Contribution |")
    o.append("|:--|:--|")
    o.append("| *Waiting for its first name.* | |")
    o.append("")
    o.append("<!-- CONTRIBUTORS:END -->")
    o.append("")
    o.append("### Recognition")
    o.append("")
    o.append("- **Named on the wall**, with a link to wherever you want it pointed.")
    o.append("- **Credited on the question** — merged questions carry their contributor's name on the platform.")
    o.append("- **Authorship preserved** — we merge, we don't squash your name away.")
    o.append("")
    o.append("Published under [CC BY 4.0](LICENSE), so anything you contribute stays freely reusable by everyone, with attribution — including by you.")
    o.append("")
    return "\n".join(o)


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def build() -> str:
    metas = [json.loads((DATA / f).read_text(encoding="utf-8")) for f in LISTS]
    more = json.loads((DATA / MORE).read_text(encoding="utf-8"))
    total_q = sum(m["count"] for m in metas)
    total_min = sum(m["total_minutes"] for m in metas)

    names = [m["name"] for m in metas]
    h_ml, h_llm = f"2. {names[0]}", f"3. {names[1]}"
    h_more, h_plat = "4. Grind More", "5. Come Practice on the Platform"
    h_contrib, h_wall = "6. How to Contribute", "7. Contributors Wall"

    p = []
    p.append('<div align="center">')
    p.append("")
    p.append("# Grind List for AI/ML")
    p.append("")
    p.append(f"### {total_q} interview questions. {fmt_hours(total_min)}. Every one free to read.")
    p.append("")
    p.append("Two ordered, finite lists that take you from scattered revision to a plan you can actually finish.")
    p.append("")
    p.append(
        f'<img src="{badge("Questions", str(total_q), INDIGO)}"> '
        f'<img src="{badge("Practice", fmt_hours(total_min), VIOLET)}"> '
        f'<img src="{badge("Access", "100%25 free", EMERALD)}"> '
        f'<img src="{badge("PRs", "welcome", PINK)}"> '
        f'<img src="{badge("License", "CC BY 4.0", SLATE)}">'
    )
    p.append("")
    p.append(
        f'<b><a href="#{anchor(h_ml)}">Grind 75 ML</a> · '
        f'<a href="#{anchor(h_llm)}">Grind 75 LLM</a> · '
        f'<a href="#{anchor(h_more)}">Grind More</a> · '
        f'<a href="#{anchor(h_plat)}">Practice</a> · '
        f'<a href="#{anchor(h_contrib)}">Contribute</a></b>'
    )
    p.append("")
    p.append("</div>")
    p.append("")
    p.append("---")
    p.append("")

    p.append("## 1. Contents")
    p.append("")
    p.append("| | Section | What's in it |")
    p.append("|:--|:--|:--|")
    for i, m in enumerate(metas):
        h = f'{2+i}. {m["name"]}'
        d = m.get("difficulty", {})
        p.append(f'| **{2+i}** | [{m["name"]}](#{anchor(h)}) | {m["count"]} questions · '
                 f'{fmt_hours(m["total_minutes"])} · {d.get("Easy",0)}/{d.get("Medium",0)}/{d.get("Hard",0)} E·M·H |')
    p.append(f'| **4** | [Grind More](#{anchor(h_more)}) | {more["count"]} further questions across {len(more["groups"])} areas |')
    p.append(f'| **5** | [Come Practice on the Platform](#{anchor(h_plat)}) | Design studio, coding platform, answer marking |')
    p.append(f'| **6** | [How to Contribute](#{anchor(h_contrib)}) | Templates, quality bar, review process |')
    p.append(f'| **7** | [Contributors Wall](#{anchor(h_wall)}) | Who built this |')
    p.append("")
    p.append("> **How to use this**  \n"
             "> Fork the repo and tick boxes off in your own copy. The lists are sequenced, "
             "not sorted by difficulty — work top to bottom. The time next to each question "
             "is roughly what a solid *spoken* answer takes; if you run well over, that's the "
             "gap to study.")
    p.append("")
    p.append("---")
    p.append("")

    for i, m in enumerate(metas):
        p.append(render_list_section(2 + i, m)); p.append("---"); p.append("")
    p.append(render_more_section(4, more)); p.append("---"); p.append("")
    p.append(render_platform_section(5)); p.append("---"); p.append("")
    p.append(render_contributing_section(6)); p.append("---"); p.append("")
    p.append(render_contributors_section(7)); p.append("---"); p.append("")

    p.append('<div align="center">')
    p.append("")
    p.append(f"**Maintained by [123ofAI]({site_url('/', 'about')})** — AI/ML interview preparation: "
             "questions, mock interviews, ML system design and verified engineering case studies.")
    p.append("")
    p.append(f"Questions about contributing? **{CONTACT_EMAIL}**")
    p.append("")
    p.append("</div>")
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
            print("README.md is stale — run: python3 scripts/generate_readme.py", file=sys.stderr)
            return 1
        print("README.md is up to date.")
        return 0

    README.write_text(content, encoding="utf-8")
    print(f"Wrote {README.relative_to(ROOT)} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
