---
# A complete, filled-in Q&A submission. Copy Template_QnA.md, not this file —
# this one exists so you can see what "good" looks like before you write yours.
#
# Note what makes it acceptable: the question is one an interviewer actually
# asks out loud, the Key Takeaway would satisfy them in 30 seconds, the Deep
# Dive explains the trade-off rather than restating the definition, and the
# source is stated plainly.

type: qna

topic: classical-ml
sub_topic: Supervised Learning
level: Medium
time_minutes: 10
company_tag: ""
---

## Question

Why would you use the kernel trick in an SVM, and what does it actually cost you?

## Key Takeaway

The kernel trick lets an SVM find a linear boundary in a high-dimensional space
without ever computing the coordinates in that space — you only ever evaluate a
kernel function on pairs of points. It buys you non-linear decision boundaries
at roughly the cost of a linear model's formulation, but the cost lands at
prediction time and on memory, because the model has to keep its support vectors.

## Deep Dive

An SVM's optimisation only ever touches the data through inner products between
pairs of points. That is the whole opening: if a function `K(x, z)` equals the
inner product of `x` and `z` after some mapping into a higher-dimensional space,
you can substitute `K` wherever the inner product appears and get the benefit of
that space without constructing it. An RBF kernel corresponds to an
infinite-dimensional space, which you plainly could not build explicitly.

The costs are real and are what interviewers usually probe for:

- **Prediction is no longer O(features).** A linear SVM collapses to a single
  weight vector. A kernelised one must evaluate `K` between the query point and
  every retained support vector, so inference scales with the number of support
  vectors — which grows with dataset size and noise.
- **Training scales badly.** The kernel matrix is n x n, so memory is quadratic
  in the number of training examples. Past roughly 10^5 points this stops being
  practical without approximation.
- **You have added hyperparameters.** RBF introduces gamma alongside C, and the
  two interact: a large gamma with a large C will fit the training set almost
  perfectly and generalise poorly.

The practical answer to "when would you not use it" is: when the data is
already linearly separable in feature space, when the dataset is large enough
that the quadratic kernel matrix dominates, or when inference latency matters
more than the last point of accuracy. In those cases a linear SVM, or a
tree-based model, is usually the better trade.

## Code Example

```python
from sklearn.svm import SVC
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split

# Two concentric circles: no linear boundary exists in the original 2-D space.
X, y = make_circles(n_samples=500, factor=0.4, noise=0.08, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)

linear = SVC(kernel="linear").fit(X_tr, y_tr)
rbf = SVC(kernel="rbf", gamma="scale", C=1.0).fit(X_tr, y_tr)

print(f"linear : {linear.score(X_te, y_te):.2f}")          # ~0.50, no better than chance
print(f"rbf    : {rbf.score(X_te, y_te):.2f}")             # ~1.00
print(f"support vectors kept: {len(rbf.support_)}")        # the inference cost
```

## Source

Asked in a 2026 ML engineer interview; the follow-up was "and what breaks when
you have a million rows?", which is why the cost side is written out above.
