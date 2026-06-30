# Linear Algebra Intuition Cheat Sheet

| Concept | Geometric Meaning |
|---------|-------------------|
| **Matrix** | A linear transformation. It maps vectors from one space to another while preserving lines and linearity. |
| **Rank** | The number of independent directions that survive the transformation. Equivalently, the dimension of the column space. |
| **Column Space** | The set of all possible outputs $Ax$. Every output vector lies in the column space. |
| **Determinant** | How much the transformation scales area (in 2D), volume (in 3D), or hypervolume (in higher dimensions). The sign indicates whether orientation is preserved or reversed. |
| **Singular Matrix** | A transformation that squashes at least one dimension completely, causing the area/volume to become zero. Information is lost, so the transformation cannot be undone. |
| **Inverse Matrix** | The transformation that exactly undoes the original transformation. It exists only when the original transformation loses no information (i.e., the matrix is full rank and square). |

---

## One-Sentence Summary

- **Matrix** → A machine that transforms vectors.
- **Rank** → How many independent directions remain after the transformation.
- **Column Space** → All vectors that the transformation can produce.
- **Determinant** → How much space (area/volume) is stretched or compressed.
- **Singular Matrix** → A transformation that collapses some dimension and loses information.
- **Inverse** → The machine that perfectly reverses the original transformation.