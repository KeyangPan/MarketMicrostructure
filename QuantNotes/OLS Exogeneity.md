# Exogeneity: Prediction vs. Causal Inference

Intuition for the exogeneity assumption, why it matters, and how it draws the line between prediction and causal inference.

## The Exogeneity Assumption

### Mathematical Definition

The exogeneity assumption is

$$E[\varepsilon \mid X] = 0.$$

This means:

> After conditioning on the regressors, the average error term is zero.

Equivalently: knowing the value of $X$ should not give us any information about the average value of the omitted factors contained in $\varepsilon$.

### Why is it Called Exogeneity?

The word **exogeneity** comes from Greek:

- **exo-** = outside
- **-genous** = generated

Literally,

> **generated from outside.**

The opposite is **endogeneity**, meaning

> **generated from within the system.**

The intuition is that the regressor $X$ should be determined **outside** the part of the world captured by the error term $\varepsilon$. In other words, none of the omitted factors inside $\varepsilon$ should influence how $X$ is generated.

### A Modern Causal Interpretation

A useful way to think about exogeneity is through **randomized experiments**.

Imagine education were assigned completely at random (like flipping a coin to decide whether someone stays in school for an extra year). Then education would be unrelated to intelligence, motivation, family background, or any other omitted factors.

In this case, education is **generated externally** to the rest of the system, so it is exogenous:

$$E[\varepsilon \mid X] = 0.$$

Randomized Controlled Trials (RCTs) are considered the gold standard for causal inference because randomization creates exogeneity by construction.

### What is the Error Term?

Suppose the true model is

$$Y = \beta_1 X + \beta_2 Z + u,$$

where $X$ is observed, $Z$ is omitted, and $u$ is random noise. If we fit the simplified model $Y = \beta X + \varepsilon$, then

$$\varepsilon = \beta_2 Z + u.$$

The error term is **not** simply random noise. Instead:

> The error term contains everything that affects $Y$ but is not included in the regression model.

Examples include:

- Omitted variables
- Measurement error
- Unobserved heterogeneity
- Luck
- Random shocks

---

## Intuition Behind Exogeneity

Imagine we are studying

$$\text{Salary} = \beta \cdot \text{Education} + \varepsilon,$$

where

$$\varepsilon = \text{Ability} + \text{Motivation} + \text{Luck} + \cdots$$

The key question becomes:

> Does knowing someone's education tell us something about their omitted characteristics?

If **no**, then $E[\varepsilon \mid \text{Education}] = 0$ and exogeneity holds.

If **yes**, then $E[\varepsilon \mid \text{Education}] \neq 0$ and exogeneity is violated.

### Example: Ability

Suppose more intelligent people tend to obtain more education:

$$\text{Higher Ability} \;\longrightarrow\; \text{Higher Education}, \qquad \text{Higher Ability} \;\longrightarrow\; \text{Higher Salary}.$$

Ability is omitted from the regression, so Ability is inside $\varepsilon$. Since Ability is correlated with Education, Education is correlated with the error term — this violates exogeneity.

---

## Why Does This Damage OLS?

OLS assumes that any relationship between $X$ and $Y$ comes from the coefficient $\beta$. But if $X \longrightarrow \varepsilon$, then part of the relationship between $X$ and $Y$ actually comes from omitted variables.

OLS cannot distinguish:

- The **direct** effect of $X$, and
- The **indirect** effect through omitted variables.

As a result, the estimated coefficient absorbs both effects, and the estimate becomes biased.

### A Simple Example

Suppose the true model is

$$\text{Salary} = 2000 \times \text{Education} + 5000 \times \text{Ability},$$

and further suppose $\text{Ability} = \text{Education}$. Then

$$\text{Salary} = 7000 \times \text{Education},$$

so OLS estimates $\hat{\beta} = 7000$.

But notice what happened. The true causal effect of education is only **\$2000**; the remaining **\$5000** comes from ability. OLS has combined both effects into a single coefficient.

---

## The Key Insight

The important question is not

> "Is the coefficient mathematically wrong?"

Instead, ask

> "What quantity is the coefficient actually estimating?"

This leads to one of the most important distinctions in econometrics.

---

## Prediction vs. Causal Inference

Although the same regression model is used, there are two fundamentally different questions.

### Question 1: Prediction (Association)

> If I observe someone with one additional year of education, how much higher is their expected salary?

Mathematically,

$$E[Y \mid X = x+1] - E[Y \mid X = x].$$

This is purely observational. Everything that moves together with education is part of the answer — education, ability, family background, motivation, and so on. Therefore the OLS coefficient measures the **total association**. For prediction, this is often exactly what we want.

### Question 2: Causal Inference

> Suppose I magically increase one person's education by one year while keeping everything else exactly the same. How much would their salary increase?

This is the **causal effect**. Here Ability, Family Background, Motivation, etc. are all held fixed, and only Education changes. This is the quantity represented by $\beta$ in the structural model. Recovering it requires exogeneity.

---

## Why Econometricians Care About Exogeneity

- If exogeneity **holds**, OLS estimates the causal effect.
- If exogeneity **fails**, OLS estimates the observational association instead — the coefficient is no longer purely causal.

---

## Machine Learning vs. Econometrics

This distinction explains a major philosophical difference between the two fields.

- Machine learning typically asks: *"Can I predict $Y$ accurately?"*
- Econometrics often asks: *"What would happen if I intervened and changed $X$?"*

These are different objectives. For prediction, an omitted variable that improves predictive accuracy is not necessarily a problem. For causal inference, the same omitted variable can completely invalidate the interpretation of the coefficient.

---

## Quant Finance Example

Suppose

$$\text{FutureReturn} = \beta \cdot \text{OrderImbalance} + \varepsilon,$$

and assume institutional demand both creates order imbalance and pushes prices upward. Institutional demand is omitted, so it sits inside $\varepsilon$.

- Goal: *"Can order imbalance predict future returns?"* → the OLS coefficient is still useful.
- Goal: *"Does order imbalance itself cause prices to move?"* → the coefficient is contaminated by omitted institutional demand.

The predictive relationship remains useful, but the causal interpretation is no longer valid.

---

## Summary

The exogeneity assumption is fundamentally about **interpretation, not computation**.

Without exogeneity, OLS still estimates a meaningful quantity: the observational association between $X$ and $Y$. However, it generally no longer estimates the causal effect of $X$.

The key question is therefore not

> "Is OLS wrong?"

but rather

> "Is OLS estimating the quantity that I actually care about?"

This is the central distinction between prediction and causal inference, and one of the foundational ideas of modern econometrics.