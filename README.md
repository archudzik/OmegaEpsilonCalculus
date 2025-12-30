# Ωε-Calculus

Reference implementation of the Ωε-calculus, a total term-rewriting system with distinguished constants governing symbolic resolution.

## Overview

The calculus introduces two constants, Ω and ε, governed by the rewrite rule ε · Ω → 1. All operations are total: every ground term reduces to a unique normal form. Expressions traditionally regarded as undefined (such as 1/0 or 0/0) are treated as well-formed terms with specified rewrite behavior.

## Requirements

- Python 3.x

## Installation

No external dependencies required. Clone the repository:

```
git clone https://github.com/archudzik/OmegaEpsilonCalculus.git
cd OmegaEpsilonCalculus
```

## Usage

Run the demonstration:

```
python model.py
```

## Output

```
=== Ωε-CALCULUS ===

Primitive rules:
         1 / 0  →  Ω
         1 / Ω  →  ε
         ε · Ω  →  1
         Ω · ε  →  1
         0 · Ω  →  0

Power and scaling rules:
         Ω · Ω  →  Ω²
         Ω / ε  →  Ω²
        ε · Ω³  →  Ω²
   (3/2·Ω) · ε  →  3/2

Closure (no undefined forms):
         0 / 0  →  0
         Ω / Ω  →  1
         ε / ε  →  1
```

## Rewrite Rules

### Primitive Rules

| Rule      | Description                |
| --------- | -------------------------- |
| 1 / 0 → Ω | Division by zero yields Ω  |
| 1 / Ω → ε | Reciprocal of Ω is ε       |
| ε · Ω → 1 | Core identity              |
| 0 · t → 0 | Zero absorption            |
| 0 / 0 → 0 | Closure                    |
| t / t → 1 | Self-division (t ∈ {Ω, ε}) |

### Power and Scaling Rules

| Rule            | Description             |
| --------------- | ----------------------- |
| Ω · Ω → Ω²      | Power formation         |
| Ωᵐ · Ωⁿ → Ωᵐ⁺ⁿ  | Power combination       |
| ε · Ωⁿ → Ωⁿ⁻¹   | Power reduction (n ≥ 2) |
| Ω / ε → Ω²      | Division by ε           |
| (c · Ω) · ε → c | Scaled collapse (c ∈ ℚ) |

## External Interpretation

The calculus admits external interpretations. Given a resolution unit δ > 0:

```
⟦ε⟧ = δ,  ⟦Ω⟧ = 1/δ
```

For example, taking δ as the Planck length (≈ 1.616 × 10⁻³⁵ m) yields Ω as the number of Planck lengths per meter.

## License

This project is licensed under the MIT License.

## Citation

If you use this work, please cite:

```
@misc{chudzik2025omegaepsilon,
  author = {Chudzik, Artur},
  title = {The Ωε-Calculus},
  year = {2025},
  url = {https://github.com/archudzik/OmegaEpsilonCalculus}
}
```
