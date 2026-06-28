# Regression with Overlapping Labels, Autocorrelated Errors, and GLS

**Author:** Keyang Pan
**Last updated:** 2026-06-27

---

## 1. Motivation

Suppose we run a regression on high-frequency data, observed **every tick**, with
the target

$$
y_t = \log(M_{t+n}) - \log(M_t)
$$

where $M_t$ is the mid-price and $n$ is the prediction horizon (e.g. 100 ticks).

The problem is that consecutive labels **overlap heavily**. For example:

$$
y_t = M_{100} - M_0, \qquad y_{t+1} = M_{101} - M_1
$$

These two labels share the path $M_1, \dots, M_{100}$ — almost the entire future
window is identical. Therefore

$$
\mathrm{Corr}(y_t, y_{t+1}) \approx 1.
$$

---

## 2. Which OLS assumption is violated?

OLS assumes

$$
\mathrm{Var}(\varepsilon) = \sigma^2 I,
$$

which implies **homoskedasticity** and **no serial correlation**.

In the overlapping-label case,

$$
\mathrm{Var}(\varepsilon) = \Omega, \qquad \mathrm{Cov}(\varepsilon_t, \varepsilon_{t+k}) \neq 0.
$$

So OLS no longer satisfies the Gauss–Markov assumptions.

---

## 3. Does the OLS coefficient become wrong?

**No.** The OLS estimator

$$
\hat\beta = (X'X)^{-1} X'y
$$

is still unbiased provided exogeneity holds, $\mathbb{E}[\varepsilon \mid X] = 0$.
The coefficient estimate remains valid.

> The problem is **not bias** — it is **variance estimation**.

---

## 4. What becomes wrong?

OLS reports

$$
\mathrm{Var}(\hat\beta) = \sigma^2 (X'X)^{-1},
$$

which is only true when $\mathrm{Var}(\varepsilon) = \sigma^2 I$. The correct
("sandwich") variance is

$$
\mathrm{Var}(\hat\beta) = (X'X)^{-1}\, X'\,\Omega\, X\, (X'X)^{-1}.
$$

Consequences of using the wrong formula:

| Quantity | Effect |
| --- | --- |
| Standard errors | Underestimated |
| t-statistics | Inflated |
| p-values | Too optimistic |
| Confidence intervals | Too narrow |

---

## 5. Effective sample size

Suppose one million ticks and a 100-tick forward return. Although there are
$N = 1{,}000{,}000$ observations, the labels overlap heavily, so the effective
number of independent observations is approximately

$$
N_{\text{eff}} \approx \frac{N}{100}.
$$

This is why overlapping labels often produce **misleadingly significant** results.

---

## 6. Solutions

### A. Decimation

Sample only every $n$-th observation ($0, 100, 200, 300, \dots$).

- **Pro:** independent labels.
- **Con:** throws away most of the data.

### B. HAC (Newey–West)

Keep all observations, estimate the covariance of the residuals, and correct
**only the standard errors**. The coefficient is unchanged.

### C. Hansen–Hodrick

Specifically designed for overlapping returns; commonly used in empirical
finance.

### D. Prediction instead of inference

If the objective is prediction rather than statistical inference, we often ignore
t-statistics entirely and evaluate with **IC, Sharpe, PnL, out-of-sample $R^2$**.

---

## 7. GLS

Given $\mathrm{Var}(\varepsilon) = \Omega$, GLS estimates

$$
\hat\beta_{\text{GLS}} = (X'\,\Omega^{-1} X)^{-1} X'\,\Omega^{-1} y.
$$

The intuition: instead of assuming independent errors, GLS **removes the
correlation first**.

---

## 8. Whitening

Find a matrix $P = \Omega^{-1/2}$ such that

$$
P\,\Omega\,P' = I.
$$

Transform the regression by multiplying through by $P$:

$$
y = X\beta + \varepsilon \quad\Longrightarrow\quad Py = PX\beta + P\varepsilon.
$$

Since $\mathrm{Var}(P\varepsilon) = I$, the transformed regression satisfies the
OLS assumptions. Run ordinary least squares on $(Py,\, PX)$.

---

## 9. Feasible GLS (FGLS)

Usually $\Omega$ is unknown. Typical workflow:

1. **Run OLS** and obtain residuals $\hat\varepsilon$.
2. **Model the residual process**, e.g.
   - AR(1): $\varepsilon_t = \rho\,\varepsilon_{t-1} + u_t$
   - MA(q), ARMA, AR-GARCH, etc.
3. **Estimate** $\hat\Omega$.
4. **Construct** $P = \hat\Omega^{-1/2}$.
5. **Whiten:** $\tilde y = P y$, $\tilde X = P X$.
6. **Run OLS again** on the whitened data.

---

## 10. Important distinction: autocorrelation vs heteroskedasticity

These are **different problems**:

| Concept | Definition | Modeled by |
| --- | --- | --- |
| Autocorrelation | $\mathrm{Cov}(\varepsilon_t, \varepsilon_{t-k}) \neq 0$ | AR / MA / ARMA |
| Heteroskedasticity | $\mathrm{Var}(\varepsilon_t)$ changes over time | GARCH |

GARCH models **time-varying (conditional) variance**, *not* serial correlation
itself. AR(1) models **serial correlation**. **AR-GARCH** models both
simultaneously.

---

## 11. Why GLS is uncommon in high-frequency finance

With a 100-tick horizon, the residuals behave approximately like an **MA(99)**
process, so the covariance matrix $\Omega$ becomes extremely large. For millions
of observations, constructing $\Omega^{-1}$ is computationally expensive.

Practitioners therefore usually prefer:

- OLS + HAC standard errors
- Hansen–Hodrick
- Time-series cross-validation
- Purged CV + embargo
- Non-overlapping test labels

rather than full GLS.

---

## 12. Key takeaways

- Overlapping labels create **serially correlated errors**.
- OLS coefficients remain **unbiased** if exogeneity holds.
- OLS **standard errors become incorrect** (too small).
- **GLS** whitens the residuals before regression; **FGLS** estimates the
  covariance structure from residuals first.
- **GARCH** models volatility, not autocorrelation.
- In quant finance, **HAC + careful backtesting** are usually preferred over full
  GLS.
