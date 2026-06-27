# Regression with Overlapping Labels, Autocorrelated Errors, and GLS

Author: Keyang Pan

Last Updated: 2026-06-27

---

# 1. Motivation

Suppose we perform a regression on high-frequency data.

Observation frequency:

- Every tick

Target:

```text
y_t = log(M_{t+n}) - log(M_t)
```

where

- M_t = mid-price
- n = prediction horizon (e.g. 100 ticks)

The problem is that consecutive labels overlap heavily.

Example:

```text
y_t     = M_100 - M_0
y_{t+1} = M_101 - M_1
```

These two labels share

```text
M_1 ... M_100
```

which means almost the entire future path is identical.

Therefore,

```text
Corr(y_t, y_{t+1}) ≈ 1
```

---

# 2. Which OLS assumption is violated?

OLS assumes

```text
Var(epsilon) = sigma^2 I
```

This implies

- Homoskedasticity
- No serial correlation

In the overlapping-label case,

```text
Var(epsilon) = Omega
```

where

```text
Cov(epsilon_t, epsilon_{t+k}) != 0
```

Therefore,

OLS no longer satisfies the Gauss-Markov assumptions.

---

# 3. Does OLS coefficient become wrong?

No.

The OLS estimator is

```text
beta_hat = (X'X)^(-1) X'y
```

It is still unbiased provided

```text
E[epsilon | X] = 0
```

The coefficient estimate remains valid.

The problem is **NOT bias**.

The problem is **variance estimation**.

---

# 4. What becomes wrong?

OLS reports

```text
Var(beta_hat)
=
sigma^2 (X'X)^(-1)
```

This is only true if

```text
Var(epsilon) = sigma^2 I
```

The correct variance is

```text
Var(beta_hat)
=
(X'X)^(-1)
X'
Omega
X
(X'X)^(-1)
```

Consequences:

- Standard errors are underestimated.
- t-statistics are inflated.
- p-values become too optimistic.
- Confidence intervals become too narrow.

---

# 5. Effective sample size

Suppose

- one million ticks
- future 100-tick return

Although there are

```text
1,000,000 observations
```

the labels overlap heavily.

The effective number of independent observations is approximately

```text
N_eff ≈ N / 100
```

This is why overlapping labels often produce misleadingly significant results.

---

# 6. Solutions

## Solution A: Decimation

Only sample every n-th observation.

Example:

```text
0
100
200
300
...
```

Pros

- Independent labels

Cons

- Throw away most data

---

## Solution B: HAC (Newey-West)

Keep all observations.

Estimate the covariance of residuals.

Correct only the standard errors.

Coefficient remains unchanged.

---

## Solution C: Hansen-Hodrick

Specifically designed for overlapping returns.

Commonly used in empirical finance.

---

## Solution D: Prediction instead of inference

If the objective is prediction rather than statistical inference,

we often ignore t-statistics completely.

Instead evaluate using

- IC
- Sharpe
- PnL
- Out-of-sample R²

---

# 7. GLS

Suppose

```text
Var(epsilon) = Omega
```

GLS estimates

```text
beta_GLS
=
(X' Omega^(-1) X)^(-1)
X' Omega^(-1) y
```

The intuition is simple:

Instead of assuming independent errors,

GLS removes the correlation first.

---

# 8. Whitening

Find a matrix

```text
P = Omega^(-1/2)
```

such that

```text
P Omega P' = I
```

Transform the regression.

Original:

```text
y = X beta + epsilon
```

Multiply by P:

```text
Py = PX beta + P epsilon
```

Since

```text
Var(P epsilon) = I
```

the transformed regression satisfies OLS assumptions.

Run ordinary least squares on

```text
(Py, PX)
```

---

# 9. Feasible GLS (FGLS)

Usually

```text
Omega
```

is unknown.

Typical workflow:

### Step 1

Run OLS.

Obtain residuals

```text
epsilon_hat
```

---

### Step 2

Model the residual process.

Examples

AR(1)

```text
epsilon_t
=
rho * epsilon_{t-1}
+
u_t
```

MA(q)

ARMA

AR-GARCH

etc.

---

### Step 3

Estimate

```text
Omega_hat
```

---

### Step 4

Construct

```text
P = Omega_hat^(-1/2)
```

---

### Step 5

Whiten

```text
y_tilde = P y

X_tilde = P X
```

---

### Step 6

Run OLS again.

---

# 10. Important distinction

Autocorrelation means

```text
Cov(epsilon_t, epsilon_{t-k}) != 0
```

Heteroskedasticity means

```text
Var(epsilon_t)
```

changes over time.

These are different problems.

GARCH models

- Time-varying variance

NOT

- Serial correlation itself

For example

AR(1)

models

- Serial correlation

GARCH

models

- Conditional variance

AR-GARCH

models both simultaneously.

---

# 11. Why GLS is uncommon in high-frequency finance

Suppose

future horizon = 100 ticks.

Residuals approximately behave like

```text
MA(99)
```

The covariance matrix

```text
Omega
```

becomes extremely large.

For millions of observations,

constructing

```text
Omega^(-1)
```

is computationally expensive.

Therefore practitioners usually prefer

- OLS + HAC standard errors
- Hansen-Hodrick
- Time-series cross validation
- Purged CV
- Embargo
- Non-overlapping test labels

rather than full GLS.

---

# 12. Key Takeaways

- Overlapping labels create serially correlated errors.
- OLS coefficients remain unbiased if exogeneity holds.
- OLS standard errors become incorrect.
- GLS attempts to whiten the residuals before regression.
- FGLS estimates the covariance structure from residuals.
- GARCH models volatility, not autocorrelation.
- In quantitative finance, HAC and careful backtesting are usually preferred over full GLS.