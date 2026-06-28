# Rolling-Window Backtest and the Hold-Out Set

Why a walk-forward (rolling-window) backtest plus a reserved hold-out set is the
right evaluation design for a factor/alpha study, and how the pieces fit
together.

## The problem we are guarding against

Financial data is **non-stationary** (relationships drift over time) and we are
desperate to avoid **look-ahead bias / overfitting to one period**. A single
in-sample fit-and-score tells us almost nothing about whether a signal will work
*out of sample, going forward* — which is the only thing that matters live.

So the evaluation has to mimic reality: **only ever predict the future using the
past, and judge the model on data it has never seen.**

---

## Part 1 — Why a rolling-window (walk-forward) backtest

A walk-forward backtest slides a window through time: train on a block of the
recent past, validate on the block immediately after, then roll forward and
repeat.

```
train[09:30–10:20] val[10:20–10:30]
train[09:40–10:30] val[10:30–10:40]
train[09:50–10:40] val[10:40–10:50]   ← train windows roll; val segments tile
...
```

### Why this design

1. **Respects the arrow of time (no leakage).** Each validation block sits
   strictly *after* its training block, so we never use future information to
   predict the past. A single random train/test split would shuffle future into
   the training set — invalid for time series.

2. **Tests robustness across regimes, not luck in one period.** Many
   train→predict cycles across the session expose whether the signal is *stable*
   (works in the morning and the afternoon, in calm and volatile stretches) or
   was a one-off fluke. One number from one split can't show this.

3. **Adapts to drift.** Refitting as the window rolls lets the model track
   changing microstructure dynamics; every prediction is made by a model fit on
   the *most recent* data, which is how a live system would actually run.

4. **Produces an out-of-sample track record, not a point estimate.** A series of
   OOS results gives a distribution: mean edge, its stability, an equity curve,
   regime dependence — far richer than a single accuracy number.

### Overlap: what is and isn't OK

- **Test/validation segments should NOT overlap** — overlapping test blocks
  reuse the same outcomes and double-count performance. We step by the
  validation length so val segments **tile** (each future point scored exactly
  once → full out-of-sample coverage of the period).
- **Training windows MAY overlap** (consecutive windows share most of their
  history). This is fine and even desirable: it maximizes data coverage and
  keeps models fresh. The only consequence is that consecutive models are
  *correlated*, so the per-window results are **not independent trials** — treat
  cross-window "consistency" as weaker evidence than N independent samples, and
  use block methods if formal significance is needed.
- **Overlap across the train→val boundary is leakage, not mere inefficiency.**
  If a training row's forward-looking label pokes into the validation period, the
  model has seen the future. This must be **purged/embargoed** (gap ≥ label
  horizon). Computing factors and labels *per slice* (so boundary rows come out
  NaN) handles this automatically.

> Related: the label-horizon overlap that shrinks effective sample size
> ($n_\text{eff}=n/h$) is a *separate* issue living inside each test segment —
> see `Regression with Overlapping Labels.md`.

---

## Part 2 — Why a separate hold-out set

Before any windowing, we carve off a final block of data (e.g. the **last
trading hour**) and lock it away. It is used **once, at the very end**, for final
reporting — never during research.

```
|<--------------- trainable (walk-forward lives here) --------------->|<-- hold-out -->|
09:30                                                              15:00            16:00
```

### Why this is necessary on top of walk-forward

1. **Walk-forward validation gets "used up" by research choices.** Across a
   project we look at the validation results many times — choosing factors,
   horizons, the λ for Lasso, window sizes. Every such decision quietly fits to
   the validation data. This is **selection bias / multiple-testing leakage**:
   the validation score slowly stops being out-of-sample because our *choices*
   were informed by it.

2. **The hold-out is the one truly untouched sample.** Because we never look at
   it while developing, the score on it is an **unbiased estimate of real-world
   performance**. It is the honest answer to "after all my tinkering, does this
   actually work?"

3. **It catches overfitting that walk-forward can't.** A strategy can look great
   across all validation windows simply because we kept tweaking until it did.
   The hold-out, seen only at the end, exposes that gap.

### The discipline that makes it work

- **Touch it exactly once**, after the model and all hyperparameters are frozen.
- If the hold-out result disappoints and we go back and re-tune, the hold-out is
  now "burned" (it informed a choice) — strictly, it should be replaced with
  fresh data. In practice, minimizing the number of hold-out peeks is the whole
  point.
- It must be the **most recent** block (the future relative to all training), to
  mirror live deployment.

---

## How the two work together

| Layer | Purpose | Touched during research? |
|---|---|---|
| **Rolling train/val windows** | model selection, hyperparameter tuning, robustness checks | Yes — repeatedly |
| **Hold-out set** | final, unbiased estimate of OOS performance | No — once at the end |

Mental model: **walk-forward is how you *develop* and stress-test the signal;
the hold-out is the final exam you only sit once.** Walk-forward keeps each step
honest about the arrow of time; the hold-out keeps the *whole project* honest
about how much you implicitly overfit while developing.

---

## One-line summary

> Use a rolling walk-forward backtest to get many leakage-free, regime-diverse
> out-of-sample evaluations for model development; reserve a final, never-touched
> hold-out set as the single unbiased read on real-world performance after all
> research choices are frozen.
