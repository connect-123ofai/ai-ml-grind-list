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

LISTS = ["grind-75-ml.json", "grind-50-llm.json"]
MORE = "grind-more.json"

CONTACT_EMAIL = "contact@aspirefrontiers.com"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def anchor(heading: str) -> str:
    """GitHub's heading-anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    a = heading.strip().lower()
    a = re.sub(r"[^\w\s-]", "", a)
    return re.sub(r"\s+", "-", a)


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


def site_url(path: str, campaign: str) -> str:
    return f"{SITE}{path}?utm_source={UTM_SOURCE}&utm_medium={UTM_MEDIUM}&utm_campaign={campaign}"


def md_cell(text: str) -> str:
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
    if q.get("pro"):
        bits.append("🔒")
    url = question_url(q["path"], campaign)
    return f'- [ ] **{q["n"]}.** [{md_cell(q["title"])}]({url}) · ' + " · ".join(bits)


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------

def render_list_section(num: int, meta: dict) -> tuple[str, str]:
    campaign = meta["slug"].replace("-", "_")
    qs = meta["questions"]
    heading = f'{num}. {meta["name"]}'
    d = meta.get("difficulty", {})
    free = sum(1 for q in qs if not q["pro"])
    coding = sum(1 for q in qs if q["type"] == "coding")

    # Sub-topic tagging: the spread is stated up front so a reader can see what
    # the list actually covers before committing 17 hours to it.
    by_sub: dict[str, list] = {}
    for q in qs:
        by_sub.setdefault(q["subtopic"], []).append(q)

    o = [f"## {heading}", ""]
    o.append(meta["description"])
    o.append("")
    o.append(
        f'**{len(qs)} questions** · **{fmt_hours(meta["total_minutes"])}** · '
        f'{d.get("Easy",0)} easy / {d.get("Medium",0)} medium / {d.get("Hard",0)} hard · '
        f"{coding} hands-on coding · {free} fully open"
    )
    o.append("")
    o.append(f'[Solve this list on 123ofAI →]({site_url("/qnalab/lists/" + meta["platform_key"], campaign)})')
    o.append("")

    o.append(f"<details open>")
    o.append(f'<summary><b>Sub-topics covered</b> — {len(by_sub)} areas</summary>')
    o.append("")
    o.append("| Sub-topic | Questions | Jump to |")
    o.append("|---|---|---|")
    for sub in sorted(by_sub, key=lambda s: (-len(by_sub[s]), s)):
        items = by_sub[sub]
        nums = " ".join(f'[{q["n"]}]({question_url(q["path"], campaign)})' for q in items[:12])
        if len(items) > 12:
            nums += f" *+{len(items) - 12} more*"
        o.append(f"| **{md_cell(sub)}** | {len(items)} | {nums} |")
    o.append("")
    o.append("</details>")
    o.append("")
    o.append("The list is sequenced — work top to bottom. Fork the repo to tick items off in your own copy.")
    o.append("")
    for q in qs:
        o.append(question_line(q, campaign))
    o.append("")
    return heading, "\n".join(o)


def render_more_section(num: int, meta: dict) -> tuple[str, str]:
    campaign = "grind_more"
    heading = f'{num}. {meta["name"]}!'
    total_available = sum(g["available"] for g in meta["groups"])
    o = [f"## {heading}", ""]
    o.append(meta["description"])
    o.append("")
    o.append(
        f'**{meta["count"]} more questions** below, hand-picked across '
        f'{len(meta["groups"])} areas — a sample of roughly '
        f"**{total_available} free questions** in the wider bank that aren't in "
        "either list above."
    )
    o.append("")
    for g in meta["groups"]:
        o.append(f'<details>')
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
    o.append(f'**[See the full question bank →]({site_url("/qnalab/generic", campaign)})**')
    o.append("")
    return heading, "\n".join(o)


def render_platform_section(num: int) -> tuple[str, str]:
    """Screenshots render only if the file is actually present, so a missing
    asset is an absent image rather than a broken one."""
    heading = f"{num}. Come Practice on the Platform"
    campaign = "platform"
    shots = [
        ("design-studio.png", "ML Design Studio",
         "Drag real components onto a canvas — feature store, model registry, "
         "serving endpoint, monitoring — and have the design scored against six "
         "segments, from data pipeline to responsible AI.",
         "/qnalab/system-design"),
        ("coding-platform.png", "Coding Platform",
         "Write and run ML code in the browser against a real test suite. "
         "NumPy and Python, no local setup, immediate pass/fail.",
         "/qnalab/mlcodingproblems"),
        ("interview-report.png", "Test Your Understanding",
         "Answer a question in your own words and get it marked — what you "
         "covered, what you missed, and what an interviewer would have "
         "followed up on.",
         "/qnalab/generic"),
    ]
    o = [f"## {heading}", ""]
    o.append(
        "Reading a question and *thinking* you could answer it is the classic "
        "prep trap. The lists above link straight into the places you can find "
        "out whether that is true."
    )
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
    return heading, "\n".join(o)


def render_contributing_section(num: int) -> tuple[str, str]:
    heading = f"{num}. How to Contribute"
    o = [f"## {heading}", ""]
    o.append(
        "These lists get better when people who actually sat the interview say "
        "what was asked. Corrections, sharper wording and genuinely new "
        "questions are all welcome."
    )
    o.append("")
    o.append("### Pick a template")
    o.append("")
    o.append("| Submitting | Use | What it's for |")
    o.append("|---|---|---|")
    o.append("| An interview question and its answer | [`Template_QnA.md`](templates/Template_QnA.md) | The common case. |")
    o.append("| A concept explainer, not a question | [`Template_Theory.md`](templates/Template_Theory.md) | Notes that teach an idea. |")
    o.append("| A problem with runnable code and tests | [`Template_Coding.md`](templates/Template_Coding.md) | In-browser coding problems. |")
    o.append("")
    o.append(
        "Every field in those templates maps one-to-one onto our question "
        "ingestion contract. That is deliberate: when a submission is approved, "
        "the fields load straight into our ingestion form and the question "
        "reaches the live bank without anyone re-typing it. **Please don't "
        "rename keys or leave required fields blank** — a submission that "
        "doesn't parse can't be loaded automatically and takes considerably "
        "longer to land."
    )
    o.append("")
    o.append("### The quality bar")
    o.append("")
    o.append("A submission is accepted when it is:")
    o.append("")
    o.append("- **Real.** Asked in an actual interview, or a concept those interviews genuinely rely on. Not invented to pad a list.")
    o.append("- **Not already covered.** Search the lists and the bank first. A rephrasing of an existing question is a duplicate.")
    o.append("- **Discriminating.** A good question separates someone who understands the idea from someone who has memorised the definition.")
    o.append("- **Answerable in the stated time.** If your own answer runs past `time_minutes`, either the estimate or the scope is wrong.")
    o.append("- **Sourced.** Say where it came from. Submissions with no stated source are declined — we can't verify them and we won't publish what we can't stand behind.")
    o.append("- **Yours to give.** Don't paste copyrighted material from books, paid courses or another site.")
    o.append("")
    o.append("The bar rises as the lists fill up. Once an area is well covered, a new question usually has to *replace* one rather than join it — say which, and why yours is better.")
    o.append("")
    o.append("### How your PR gets reviewed")
    o.append("")
    o.append(
        "Every submission is read by someone on the 123ofAI team — the same "
        "people who maintain the question bank. We check the question against "
        "the bar above, verify the technical content, and edit for clarity "
        "where it helps. Expect comments rather than a silent close: if we ask "
        "for changes, it is because we intend to merge it once they land."
    )
    o.append("")
    o.append("Outcomes are one of three: **merged**, **changes requested**, or **declined with a reason**. We don't close submissions without saying why.")
    o.append("")
    o.append("### How long it takes")
    o.append("")
    o.append(
        "Review is manual and done by a small team alongside the rest of their "
        "work, so **please be patient** — a considered review of a technical "
        "question takes longer than a rubber stamp, and that is the point."
    )
    o.append("")
    o.append(
        f"If something genuinely needs to move faster — a factual error on a "
        f"live question, a hiring deadline — email **{CONTACT_EMAIL}** with "
        "the PR link and we will pull it forward."
    )
    o.append("")
    o.append("### A few practical things")
    o.append("")
    o.append("- **One question per pull request.** Batched submissions get reviewed at the speed of their weakest entry.")
    o.append("- **Never edit `README.md`.** It is generated from `data/`. Run `python3 scripts/generate_readme.py` after changing data, and commit the result.")
    o.append("- **Corrections don't need a template.** A typo or a wrong claim can just be a PR with the fix and a one-line explanation.")
    o.append("- **Not sure it qualifies?** Open an issue and ask before writing it up.")
    o.append("- **Anonymity is fine.** `company_tag` can be left blank; we will never publish an employer you didn't name yourself.")
    o.append("")
    return heading, "\n".join(o)


def render_contributors_section(num: int) -> tuple[str, str]:
    heading = f"{num}. Contributors Wall"
    o = [f"## {heading}", ""]
    o.append(
        "Everyone below has had a question, a correction or an improvement "
        "merged into these lists. The wall is the record — it is not ordered by "
        "volume, and a single sharp correction counts."
    )
    o.append("")
    o.append("<!-- CONTRIBUTORS:START — add a row per merged contribution. -->")
    o.append("")
    o.append("| Contributor | Contribution |")
    o.append("|---|---|")
    o.append("| *This wall is waiting for its first name.* | |")
    o.append("")
    o.append("<!-- CONTRIBUTORS:END -->")
    o.append("")
    o.append("### Recognition")
    o.append("")
    o.append("- **Named on the wall** — with a link to wherever you want it pointed.")
    o.append("- **Credited on the question** — merged questions carry their contributor's name on the platform.")
    o.append("- **GitHub history** — your commits stay attributed to you; we merge, we don't squash authorship away.")
    o.append("")
    o.append(
        "These lists are published under [CC BY 4.0](LICENSE), so anything you "
        "contribute stays freely reusable by everyone, with attribution — "
        "including by you."
    )
    o.append("")
    return heading, "\n".join(o)


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def build() -> str:
    metas = []
    for f in LISTS:
        m = json.loads((DATA / f).read_text(encoding="utf-8"))
        m["platform_key"] = "Grind75ML" if m["slug"] == "grind-75-ml" else "GrindLLM50"
        metas.append(m)
    more = json.loads((DATA / MORE).read_text(encoding="utf-8"))

    total_q = sum(m["count"] for m in metas)
    total_min = sum(m["total_minutes"] for m in metas)

    sections = []
    n = 2
    for m in metas:
        sections.append(render_list_section(n, m)); n += 1
    sections.append(render_more_section(n, more)); n += 1
    sections.append(render_platform_section(n)); n += 1
    sections.append(render_contributing_section(n)); n += 1
    sections.append(render_contributors_section(n)); n += 1

    p = []
    p.append("# Grind ML — the ML & LLM interview question lists")
    p.append("")
    p.append(
        f"**Two ordered, finite lists — {total_q} questions, about "
        f"{fmt_hours(total_min)} — that take you from scattered revision to a "
        "plan you can finish.**"
    )
    p.append("")
    p.append(
        "Every question is listed here in full and links through to 123ofAI, "
        "where you can answer it and have that answer marked. Fork the repo to "
        "track your own progress."
    )
    p.append("")

    # Section 1 — contents
    p.append("## 1. Contents")
    p.append("")
    p.append("| Section | What's in it |")
    p.append("|---|---|")
    p.append(f'| [1. Contents](#{anchor("1. Contents")}) | You are here. |')
    for m in metas:
        h = f'{2 + metas.index(m)}. {m["name"]}'
        d = m.get("difficulty", {})
        p.append(
            f'| [{h}](#{anchor(h)}) | {m["count"]} questions · '
            f'{fmt_hours(m["total_minutes"])} · '
            f'{d.get("Easy",0)}/{d.get("Medium",0)}/{d.get("Hard",0)} E/M/H |'
        )
    idx = 2 + len(metas)
    p.append(f'| [{idx}. Grind More!](#{anchor(f"{idx}. Grind More")}) | {more["count"]} further questions across {len(more["groups"])} areas. |')
    p.append(f'| [{idx+1}. Come Practice on the Platform](#{anchor(f"{idx+1}. Come Practice on the Platform")}) | Design studio, coding platform, answer marking. |')
    p.append(f'| [{idx+2}. How to Contribute](#{anchor(f"{idx+2}. How to Contribute")}) | Templates, quality bar, review process. |')
    p.append(f'| [{idx+3}. Contributors Wall](#{anchor(f"{idx+3}. Contributors Wall")}) | Who built this. |')
    p.append("")
    p.append("🔒 marks a question whose worked answer is part of 123ofAI Pro. The question itself is always free to read here and on the site.")
    p.append("")
    p.append("---")
    p.append("")

    for _, body in sections:
        p.append(body)
        p.append("---")
        p.append("")

    p.append("## About")
    p.append("")
    p.append(
        f"Maintained by [123ofAI]({site_url('/', 'about')}), an AI/ML interview "
        "preparation platform — questions, mock interviews, ML system design and "
        "verified engineering case studies."
    )
    p.append("")
    p.append(f"Questions about contributing: **{CONTACT_EMAIL}**")
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
    print(f"Wrote {README.relative_to(ROOT)} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
