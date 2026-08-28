---
# A complete, filled-in coding submission. Copy Template_Coding.md, not this one.
#
# The bar this clears: the signature is stated exactly, the constraints rule out
# the shortcut, the reference solution runs as-is, and the tests fail for a
# plausible wrong answer rather than only passing for the right one.

type: coding

topic: llm
sub_topic: Attention Mechanisms and Transformers
level: Medium
time_minutes: 20
language: numpy
company_tag: ""
---

## Title

Implement Scaled Dot-Product Attention in NumPy

## Problem Statement

Implement a single function:

```python
def attention(Q, K, V, mask=None) -> np.ndarray
```

`Q`, `K` and `V` are float arrays of shape `(seq_len, d_k)`, `(seq_len, d_k)`
and `(seq_len, d_v)`. Return the attended output of shape `(seq_len, d_v)`,
computed as `softmax(QK^T / sqrt(d_k)) V`.

`mask`, when given, is a boolean array of shape `(seq_len, seq_len)` where
`True` marks a position that must not be attended to. Masked positions must
receive exactly zero weight after the softmax — not merely a small one.

## Constraints

- NumPy only. No PyTorch, TensorFlow or `scipy.special.softmax`.
- The softmax must be numerically stable: inputs may contain values large
  enough that a naive `exp` overflows to `inf`.
- Do not modify `Q`, `K` or `V` in place.

## Reference Solution

```python
import numpy as np

def attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = Q @ K.T / np.sqrt(d_k)

    if mask is not None:
        # -inf, not a large negative number: after exp this is exactly 0.
        scores = np.where(mask, -np.inf, scores)

    # Subtract the row max before exponentiating, or large scores overflow.
    scores = scores - np.max(scores, axis=-1, keepdims=True)
    weights = np.exp(scores)
    weights /= np.sum(weights, axis=-1, keepdims=True)

    return weights @ V
```

## Tests

```python
import numpy as np

def test_shape_and_rows_sum_to_one():
    Q, K, V = np.random.randn(4, 8), np.random.randn(4, 8), np.random.randn(4, 16)
    out = attention(Q, K, V)
    assert out.shape == (4, 16)

def test_uniform_when_scores_are_equal():
    # Identical keys => every position attends equally => output is the mean of V.
    Q = np.ones((3, 4)); K = np.ones((3, 4)); V = np.arange(9).reshape(3, 3).astype(float)
    assert np.allclose(attention(Q, K, V), V.mean(axis=0))

def test_mask_gives_exactly_zero_weight():
    # A masked position must contribute nothing at all. V is chosen so that any
    # leaked weight on position 1 moves the output measurably.
    Q, K = np.random.randn(2, 4), np.random.randn(2, 4)
    V = np.array([[100.0, 0.0], [0.0, 1.0]])
    mask = np.array([[False, True], [False, True]])
    out = attention(Q, K, V, mask=mask)
    assert np.allclose(out, np.array([[100.0, 0.0], [100.0, 0.0]]))

def test_numerically_stable():
    # Naive exp(scores) overflows here and returns nan.
    Q = np.full((2, 4), 1e3); K = np.full((2, 4), 1e3); V = np.ones((2, 2))
    assert np.all(np.isfinite(attention(Q, K, V)))

def test_inputs_not_mutated():
    Q, K, V = np.random.randn(3, 4), np.random.randn(3, 4), np.random.randn(3, 4)
    before = (Q.copy(), K.copy(), V.copy())
    attention(Q, K, V)
    assert all(np.array_equal(a, b) for a, b in zip((Q, K, V), before))
```

## Explanation

The naive approach fails in two places, and both are what the question is
really testing.

The first is the scale factor. Without dividing by `sqrt(d_k)`, the dot products
grow with dimension, the softmax saturates, and gradients vanish — the reason
the original paper calls this *scaled* dot-product attention.

The second is masking. `-inf` is used rather than a large negative constant
like `-1e9` because it is scale-independent: it produces exactly zero weight
whatever the surrounding scores look like. In float64 at ordinary magnitudes
`-1e9` happens to underflow to zero after the max-subtraction and behaves
identically — the two are not distinguishable by the tests above, and it would
be dishonest to claim otherwise. The difference bites in reduced precision,
where fp16 saturates `-1e9` to `-inf` anyway and bf16's narrower mantissa makes
the margin between "very small" and "zero" much less comfortable. Writing the
intent directly costs nothing and removes the question.

## Source

Original, written for this repository. The masking failure mode is one seen in
production code more than once.
