# OLS Assumptions: Consequences and Remedies

This note summarizes the five core assumptions of Ordinary Least Squares (OLS): why each is needed, what happens when it is violated, and the common remedies.

## Overview

| Assumption | Guarantees | If Violated | Typical Remedy |
|---|---|---|---|
| 1. Linearity | Model is correctly specified | Model misspecification | Feature engineering, nonlinear models |
| 2. Exogeneity ($E[\varepsilon \mid X]=0$) | Unbiased & consistent estimates | Endogeneity (biased & inconsistent) | Better controls, IV, fixed effects |
| 3. No Perfect Multicollinearity | Unique coefficient estimates | Coefficients not uniquely estimable | Remove variables, Ridge, PCA |
| 4. Homoskedasticity | OLS is BLUE; correct classical SE | Inefficient estimates; incorrect SE | Robust SE, WLS, GLS |
| 5. No Autocorrelation | Efficient estimates; correct SE | Incorrect SE; inefficient estimates | Newey-West, HAC, GLS |

---

## Assumption 1: Linearity

### Assumption

The conditional mean of the response is linear in the coefficients:

$$Y = X\beta + \varepsilon.$$

**Important:** this means linear in the **parameters**, not necessarily in the variables. For example,

$$Y = \beta_0 + \beta_1 X + \beta_2 X^2$$

is still a linear regression model.

### Why do we need it?

OLS searches for the **best linear approximation**. If the true conditional mean is not linear, OLS is estimating the wrong model.

### Consequences of violation

Suppose the true model is $Y = X^2 + \varepsilon$, but we fit $Y = \beta X + \varepsilon$. Then we get:

- Model misspecification
- Systematic residual patterns
- Poor predictions
- Coefficients that are difficult to interpret

### Common remedies

- Polynomial features
- Interaction terms
- Splines
- Generalized Additive Models (GAM)
- Tree-based methods
- Gradient Boosting
- Neural Networks

---

## Assumption 2: Exogeneity (Zero Conditional Mean)

### Assumption

$$E[\varepsilon \mid X] = 0.$$

> After conditioning on the regressors, nothing left in the error term is systematically related to the regressors.

This is **the single most important OLS assumption.**

### Why do we need it?

It guarantees both unbiasedness and consistency:

$$E[\hat{\beta}] = \beta, \qquad \hat{\beta} \xrightarrow{p} \beta.$$

So OLS is:

- Unbiased
- Consistent

### Common causes of violation

- Omitted variables
- Reverse causality
- Simultaneity
- Measurement error

These are collectively called **endogeneity**.

### Consequences

This is the only assumption whose violation fundamentally breaks OLS. The estimator becomes:

- Biased
- Inconsistent
- Invalid for causal interpretation

Even an infinite amount of data cannot fix the problem.

### Common remedies

The right fix depends on the source of endogeneity. Typical methods include:

- Adding omitted variables
- Fixed effects
- Instrumental Variables (IV)
- Difference-in-Differences
- Randomized experiments

---

## Assumption 3: No Perfect Multicollinearity

### Assumption

The design matrix must have full column rank — equivalently, $X'X$ must be invertible.

### Why do we need it?

The OLS estimator is

$$\hat{\beta} = (X'X)^{-1}X'Y.$$

If $X'X$ is singular, the inverse does not exist.

### Example

Suppose $X_2 = 2X_1$. Then infinitely many combinations of $(\beta_1, \beta_2)$ produce identical predictions, so the coefficients cannot be uniquely identified.

### Consequences

**Perfect multicollinearity:**

- OLS cannot run
- Coefficients are not identifiable

**Near multicollinearity** — OLS still works, but:

- Very unstable coefficients
- Large standard errors
- High sensitivity to small data changes

### Common remedies

- Remove redundant variables
- Principal Component Analysis (PCA)
- Ridge Regression
- Collect more diverse data

---

## Assumption 4: Homoskedasticity

### Assumption

The error variance is constant:

$$\mathrm{Var}(\varepsilon \mid X) = \sigma^2.$$

### Example of violation

Suppose $\mathrm{Var}(\varepsilon \mid X) = X^2$. Then large values of $X$ have much noisier observations.

### Consequences

OLS estimates remain **unbiased** and **consistent**, but OLS is **no longer BLUE** and the classical standard errors are incorrect. This leads to:

- Incorrect t-tests
- Incorrect p-values
- Incorrect confidence intervals

### Common remedies

Usually we keep the coefficient estimates but fix the variance estimation:

- White Robust Standard Errors
- HC0–HC3 estimators
- Cluster-Robust Standard Errors

If the variance structure is known:

- Weighted Least Squares (WLS)
- Generalized Least Squares (GLS)

---

## Assumption 5: No Autocorrelation

### Assumption

Errors are uncorrelated across observations:

$$\mathrm{Cov}(\varepsilon_i, \varepsilon_j) = 0 \quad (i \neq j).$$

### Common examples

Especially common in finance:

- Time series
- Panel data
- Overlapping returns
- High-frequency prediction

### Consequences

Assuming exogeneity still holds, OLS coefficients remain **unbiased** and **consistent**. However:

- Standard errors become incorrect
- OLS is no longer efficient

### Common remedies

- Newey-West (HAC) Standard Errors
- Hansen-Hodrick Standard Errors (overlapping returns)
- GLS
- Explicit ARMA error models

---

## Summary of Consequences

| Assumption Violated | Biased? | Inconsistent? | Wrong SE? | Inefficient? |
|---|---|---|---|---|
| Linearity | Usually | Usually | Yes | Yes |
| Exogeneity | **Yes** | **Yes** | Yes | Yes |
| Multicollinearity | No | No | Large SE | Yes |
| Heteroskedasticity | No | No | **Yes** | Yes |
| Autocorrelation\* | No | No | **Yes** | Yes |

\*Assuming exogeneity still holds.

---

## Which Assumption Is Most Important?

Only **Exogeneity** determines whether the estimated coefficients are fundamentally correct. Violating it leads to:

- Biased estimates
- Inconsistent estimates
- Invalid causal interpretation

The remaining assumptions mainly affect:

- Efficiency
- Standard errors
- Statistical inference

---

## Quant Finance Examples

| Situation | Violated Assumption | Typical Fix |
|---|---|---|
| Overlapping future returns | Autocorrelation | Hansen-Hodrick / Newey-West |
| Volatility clustering | Heteroskedasticity | Robust SE, GLS |
| Highly correlated alpha factors | Multicollinearity | Ridge, PCA |
| Missing risk factor | Exogeneity | Add controls, Fixed Effects |
| Linear model for nonlinear market behavior | Linearity | Feature engineering, nonlinear models |

---

## Mental Checklist

Whenever using OLS, ask:

1. Is the model specification approximately correct?
2. Could any omitted variables correlate with the regressors?
3. Are my regressors nearly collinear?
4. Does the error variance change across observations?
5. Are residuals correlated over time?

Most real-world regression problems can be diagnosed by identifying **which OLS assumption has been violated**.
