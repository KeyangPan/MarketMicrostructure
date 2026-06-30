# Linear Algebra Intuition Cheat Sheet

| Concept | Geometric Meaning |
|---------|-------------------|
| **Matrix** | A linear transformation. It maps vectors from one vector space to another while preserving lines, linear combinations, and the origin. |
| **Column Space** | The set of all possible outputs $Ax$. Every output produced by the transformation lies in the column space. |
| **Rank** | The number of independent directions that survive the transformation. Equivalently, the dimension of the column space. |
| **Determinant** | How much the transformation scales area (2D), volume (3D), or hypervolume (higher dimensions). The sign indicates whether orientation is preserved or reversed. |
| **Singular Matrix** | A transformation that completely squashes one or more dimensions, making the area/volume zero. Information is lost, so the transformation cannot be perfectly reversed. |
| **Inverse Matrix** | The transformation that exactly undoes the original transformation. It exists if and only if the matrix is square and full rank (no information is lost). |
| **Eigenvector** | A special direction that is **not rotated** by the transformation. It may only be stretched, shrunk, or reflected. |
| **Eigenvalue** | The stretching (or shrinking/reflection) factor associated with an eigenvector. If $Av = \lambda v$, then the direction stays the same while the length changes by $|\lambda|$. |
| **Singular Value** | The amount of stretching along the principal orthogonal directions of the transformation. Singular values are always non-negative and equal to the square roots of the eigenvalues of $A^\top A$. |
| **SVD (Singular Value Decomposition)** | Every linear transformation can be decomposed into **Rotate (or Reflect) → Stretch/Shrink → Rotate (or Reflect)**: $A = U\Sigma V^\top$. |

---

# Relationships Between Concepts

```text
Matrix
   │
   ▼
Linear Transformation
   │
   ├──► Column Space
   │        └── All possible outputs
   │
   ├──► Rank
   │        └── Number of independent directions preserved
   │
   ├──► Determinant
   │        └── Area / volume scaling
   │
   ├──► Singular?
   │        └── Dimension collapses → determinant = 0 → no inverse
   │
   └──► Eigenvectors & Eigenvalues
            └── Special directions and their stretching factors
                     │
                     ▼
                    SVD
                     │
                     ▼
      Rotate → Stretch/Shrink → Rotate
```

---

# One-Sentence Summary

- **Matrix** → A machine that transforms vectors.
- **Column Space** → All vectors that the machine can produce.
- **Rank** → How many independent directions survive the transformation.
- **Determinant** → How much space (area/volume) is stretched or compressed.
- **Singular Matrix** → A transformation that collapses one or more dimensions and loses information.
- **Inverse** → The machine that perfectly reverses the transformation.
- **Eigenvector** → A direction that does not rotate.
- **Eigenvalue** → How much that direction is stretched or shrunk.
- **Singular Value** → The principal stretching amounts of the transformation.
- **SVD** → Every matrix is just **Rotate → Stretch/Shrink → Rotate**.

---

# Why These Concepts Matter for OLS

| OLS Object | Geometric Interpretation |
|------------|--------------------------|
| $X$ | Maps regression coefficients $\beta$ into the observation space. |
| Column Space of $X$ | All possible fitted values $X\beta$. |
| OLS | Projects $y$ orthogonally onto the column space of $X$. |
| $X^\top X$ | Describes the geometry (angles and lengths) of the predictors. |
| $(X^\top X)^{-1}$ | Corrects for the overlap between predictors by "undoing" the geometry of $X^\top X$. |
| Small Singular Values | Predictors are nearly collinear, making coefficient estimation unstable. |
| Large Entries in $(X^\top X)^{-1}$ | Small singular values become reciprocals, inflating the variance of $\hat{\beta}$. |