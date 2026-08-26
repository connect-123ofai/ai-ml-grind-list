---
# ---------------------------------------------------------------------------
# Q&A question submission
#
# Every field below maps 1:1 onto the 123ofAI question ingestion contract, so an
# approved submission can be converted straight into an ingestion document with
# no re-typing and no judgement calls in between. Please do not rename keys or
# leave a required one blank — a submission that does not parse cannot be
# auto-loaded and goes to the back of the manual queue.
# ---------------------------------------------------------------------------

type: qna                      # qna | theory | coding  (this file: qna)

topic: classical-ml            # REQUIRED. One of the topic keys listed below.
sub_topic: Supervised Learning # REQUIRED. Free text, title case.
level: Medium                  # REQUIRED. Easy | Medium | Hard
time_minutes: 10               # REQUIRED. Minutes for a solid spoken answer.
company_tag: ""                # OPTIONAL. Company you were asked this at.
                               # Leave "" if you would rather not say.

# Topic keys currently in the bank:
#   classical-ml  deep-learning  nlp  llm  computer-vision
#   mlops  probability  linear-algebra  agents  system-design
---

## Question

<!-- One question. Plain prose, no numbering, no "Q:" prefix. End with a
     question mark. Keep it to what an interviewer would actually say out
     loud. -->

## Key Takeaway

<!-- The short answer — the two or three sentences that would satisfy an
     interviewer if you had 30 seconds. This part is shown for free. -->

## Deep Dive

<!-- The full explanation. Why it works, when it breaks, what the trade-off
     is. Assume the reader knows the basics of the topic but not this
     specific thing. -->

## Code Example

<!-- OPTIONAL. Delete this heading entirely if the question is not a coding
     one. Use a fenced block with the language tag. -->

```python
# your code here
```

## Source

<!-- REQUIRED. Where this question came from: "asked in a 2026 interview at
     <company>", a public post you are permitted to quote, or your own
     original writing. Submissions with no stated source are declined —
     see the quality bar in the README. -->
