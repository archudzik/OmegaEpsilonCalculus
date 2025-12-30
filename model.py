"""Ωε-calculus reference implementation"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Union, Any

__all__ = [
    "Zero", "Omega", "Epsilon", "ScaledOmega", "PowerOmega",
    "InfinityLevel", "Rational", "Symbolic", "sym",
    "ZERO", "OMEGA", "EPSILON", "ONE",
]


class Symbolic:
    def _binary_op(self, other: Any, op: str):
        fn = getattr(self, f"_{op}", None)
        if fn:
            return fn(other)
        if isinstance(other, Symbolic):
            rfn = getattr(other, f"_{op}", None)
            if rfn:
                return rfn(self)
        return NotImplemented

    def __add__(self, other): return self._binary_op(other, "add")
    __radd__ = __add__
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return (-self) + other
    def __mul__(self, other): return self._binary_op(other, "mul")
    __rmul__ = __mul__
    def __truediv__(self, other): return self._binary_op(other, "div")
    def __rtruediv__(self, other): return sym(other) / self

    def __pow__(self, exp: int):
        if not isinstance(exp, int):
            raise TypeError("Exponent must be integer.")
        if exp < 0:
            return (self ** (-exp)).reciprocal()
        result: Symbolic = ONE
        for _ in range(exp):
            result = result * self
        return result

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._cmp_value() == other._cmp_value()

    def __hash__(self):
        return hash((self.__class__.__name__, self._cmp_value()))

    def __neg__(self): raise NotImplementedError
    def reciprocal(self): return ONE / self
    def _cmp_value(self): raise NotImplementedError
    def __str__(self): raise NotImplementedError
    def __repr__(self): return str(self)


class Zero(Symbolic):
    __slots__ = ()
    def __neg__(self): return self
    def _add(self, other): return other
    def _mul(self, other): return self

    def _div(self, other):
        return self

    def reciprocal(self): raise ZeroDivisionError("1/0 → Ω")
    def _cmp_value(self): return 0
    def __str__(self): return "0"


class Omega(Symbolic):
    __slots__ = ()
    def __neg__(self): return self

    def _add(self, other): return self

    def _mul(self, other):
        if isinstance(other, Epsilon):
            return ONE
        if isinstance(other, Zero):
            return ZERO
        if isinstance(other, Rational):
            return OMEGA if other.value == 1 else ScaledOmega(other.value)
        if isinstance(other, ScaledOmega):
            return ScaledOmega(other.coefficient)
        if isinstance(other, Omega):
            return PowerOmega(2)
        if isinstance(other, PowerOmega):
            return PowerOmega(other.exponent + 1)
        return self

    def _div(self, other):
        if isinstance(other, Omega):
            return ONE
        if isinstance(other, Epsilon):
            return PowerOmega(2)
        return self

    def reciprocal(self): return EPSILON
    def _cmp_value(self): return 1
    def __str__(self): return "Ω"


class Epsilon(Symbolic):
    __slots__ = ()
    def __neg__(self): return self

    def _add(self, other):
        if isinstance(other, (Omega, Rational, ScaledOmega, PowerOmega)):
            return other
        if isinstance(other, (Zero, Epsilon)):
            return self
        return other

    def _mul(self, other):
        if isinstance(other, Omega):
            return ONE
        if isinstance(other, Zero):
            return ZERO
        if isinstance(other, Epsilon):
            return self
        if isinstance(other, ScaledOmega):
            return Rational(other.coefficient)
        if isinstance(other, Rational):
            return self
        if isinstance(other, PowerOmega):
            return OMEGA if other.exponent == 2 else PowerOmega(other.exponent - 1)
        return self

    def _div(self, other):
        if isinstance(other, Omega):
            return ZERO
        if isinstance(other, Epsilon):
            return ONE
        return ZERO

    def reciprocal(self): return OMEGA
    def _cmp_value(self): return -1
    def __str__(self): return "ε"


@dataclass(frozen=True)
class ScaledOmega(Symbolic):
    coefficient: Fraction

    def __post_init__(self):
        if self.coefficient == 0:
            raise ValueError("Coefficient cannot be zero.")

    def __neg__(self): return self

    def _add(self, other):
        if isinstance(other, ScaledOmega) and other.coefficient == self.coefficient:
            return self
        return OMEGA

    def _mul(self, other):
        if isinstance(other, Epsilon):
            return Rational(self.coefficient)
        if isinstance(other, Rational):
            return ScaledOmega(self.coefficient * other.value)
        if isinstance(other, Zero):
            return ZERO
        return self

    def _div(self, other):
        if isinstance(other, Epsilon):
            return self * OMEGA
        if isinstance(other, ScaledOmega):
            if other.coefficient == self.coefficient:
                return ONE
            return ScaledOmega(self.coefficient / other.coefficient)
        if isinstance(other, Rational):
            return ScaledOmega(self.coefficient / other.value)
        return self

    def reciprocal(self): return EPSILON / Rational(self.coefficient)
    def _cmp_value(self): return (2, self.coefficient)
    def __str__(
        self): return f"{self.coefficient}·Ω" if self.coefficient != 1 else "Ω"


@dataclass(frozen=True)
class PowerOmega(Symbolic):
    exponent: int

    def __post_init__(self):
        if self.exponent < 2:
            raise ValueError("Exponent must be ≥ 2.")

    def __neg__(self): return self
    def _add(self, other): return self
    __radd__ = _add

    def _mul(self, other):
        if isinstance(other, Zero):
            return ZERO
        if isinstance(other, Epsilon):
            return OMEGA if self.exponent == 2 else PowerOmega(self.exponent - 1)
        if isinstance(other, Omega):
            return PowerOmega(self.exponent + 1)
        if isinstance(other, PowerOmega):
            return PowerOmega(self.exponent + other.exponent)
        if isinstance(other, ScaledOmega):
            return ScaledOmega(other.coefficient) * self
        return self
    __rmul__ = _mul

    def _div(self, other):
        if isinstance(other, PowerOmega):
            if self.exponent == other.exponent:
                return ONE
            diff = self.exponent - other.exponent
            return PowerOmega(diff) if diff > 1 else OMEGA
        if isinstance(other, Epsilon):
            return PowerOmega(self.exponent + 1)
        return self

    def reciprocal(self): return ZERO
    def _cmp_value(self): return ("Ω^", self.exponent)

    def __str__(self):
        sup = {2: "²", 3: "³"}.get(self.exponent, f"^{self.exponent}")
        return f"Ω{sup}"


@dataclass(frozen=True)
class Rational(Symbolic):
    value: Fraction

    def __neg__(self): return Rational(-self.value)

    def _add(self, other):
        if isinstance(other, Rational):
            return Rational(self.value + other.value)
        if isinstance(other, Zero):
            return self
        return other + self

    def _mul(self, other):
        if isinstance(other, Rational):
            return Rational(self.value * other.value)
        if isinstance(other, Zero):
            return ZERO
        if isinstance(other, Omega):
            return OMEGA if self.value == 1 else ScaledOmega(self.value)
        if isinstance(other, ScaledOmega):
            return ScaledOmega(self.value * other.coefficient)
        return other * self

    def _div(self, other):
        if isinstance(other, Rational):
            if other.value == 0:
                return OMEGA
            return Rational(self.value / other.value)
        if isinstance(other, Zero):
            return OMEGA
        return self * other.reciprocal()

    def reciprocal(self):
        if self.value == 0:
            return OMEGA
        return Rational(1 / self.value)

    def _cmp_value(self): return self.value
    def __str__(self): return str(self.value)


@dataclass(frozen=True)
class InfinityLevel(Symbolic):
    level: int

    def __post_init__(self):
        if self.level < 1:
            raise ValueError("Level must be ≥ 1.")

    def __neg__(self): return self

    def __lt__(self, other):
        if isinstance(other, InfinityLevel):
            return self.level < other.level
        return False

    def _add(self, other):
        if isinstance(other, InfinityLevel):
            return self if self.level >= other.level else other
        return self
    __radd__ = _add

    def _mul(self, other):
        if isinstance(other, InfinityLevel):
            return InfinityLevel(self.level + other.level)
        return self
    __rmul__ = _mul

    def _div(self, other):
        if isinstance(other, InfinityLevel):
            if self.level == other.level:
                return ONE
            diff = self.level - other.level
            return InfinityLevel(diff) if diff > 0 else ZERO
        return self

    def reciprocal(self): return ZERO
    def _cmp_value(self): return self.level
    def __str__(self): return f"∞_{self.level}"


ZERO = Zero()
OMEGA = Omega()
EPSILON = Epsilon()
ONE = Rational(Fraction(1))


def sym(x: Union[int, float, str, Fraction, Symbolic]) -> Symbolic:
    if isinstance(x, Symbolic):
        return x
    if isinstance(x, Fraction):
        return Rational(x)
    if isinstance(x, int):
        return Rational(Fraction(x))
    if isinstance(x, float):
        return Rational(Fraction(x).limit_denominator())
    if isinstance(x, str):
        s = x.strip()
        if s == "0":
            return ZERO
        if s == "Ω":
            return OMEGA
        if s == "ε":
            return EPSILON
        if s.startswith("∞_"):
            return InfinityLevel(int(s.split("_")[1]))
        if "Ω" in s:
            coef_str = s.replace("Ω", "").replace("·", "")
            coef = Fraction(coef_str) if coef_str else Fraction(1)
            return OMEGA if coef == 1 else ScaledOmega(coef)
        return Rational(Fraction(s))
    raise TypeError(f"Cannot convert {x!r} to Symbolic.")


def _test() -> None:
    assert ONE / ZERO == OMEGA
    assert ONE / OMEGA == EPSILON
    assert EPSILON * OMEGA == ONE
    assert OMEGA * EPSILON == ONE
    assert ZERO * OMEGA == ZERO
    assert ONE / EPSILON == OMEGA
    assert OMEGA / EPSILON == PowerOmega(2)
    assert OMEGA * OMEGA == PowerOmega(2)
    assert EPSILON * PowerOmega(3) == PowerOmega(2)
    i1, i2, i3 = InfinityLevel(1), InfinityLevel(2), InfinityLevel(3)
    assert i1 < i2 < i3
    assert sym(5) == sym(Fraction(5, 1))
    assert OMEGA == sym("Ω")
    assert InfinityLevel(2) + InfinityLevel(5) == InfinityLevel(5)
    assert InfinityLevel(2) * InfinityLevel(3) == InfinityLevel(5)
    x = sym(7)
    assert (x * OMEGA) * EPSILON == x
    so = ScaledOmega(Fraction(3, 2))
    assert so * EPSILON == Rational(Fraction(3, 2))
    # Closure: no undefined forms
    assert ZERO / ZERO == ZERO
    assert OMEGA / OMEGA == ONE
    assert EPSILON / EPSILON == ONE
    assert PowerOmega(2) / PowerOmega(2) == ONE
    assert InfinityLevel(2) / InfinityLevel(2) == ONE
    print("All tests passed.")


def _demo() -> None:
    print("=== Ωε-CALCULUS ===\n")

    print("Primitive rules:")
    pairs = [
        ("1 / 0", ONE / ZERO),
        ("1 / Ω", ONE / OMEGA),
        ("ε · Ω", EPSILON * OMEGA),
        ("Ω · ε", OMEGA * EPSILON),
        ("0 · Ω", ZERO * OMEGA),
    ]
    for label, value in pairs:
        print(f"  {label:>12}  →  {value}")

    print("\nPower and scaling rules:")
    pairs = [
        ("Ω · Ω", OMEGA * OMEGA),
        ("Ω / ε", OMEGA / EPSILON),
        ("ε · Ω³", EPSILON * PowerOmega(3)),
        ("(3/2·Ω) · ε", ScaledOmega(Fraction(3, 2)) * EPSILON),
    ]
    for label, value in pairs:
        print(f"  {label:>12}  →  {value}")

    print("\nClosure (no undefined forms):")
    closure = [
        ("0 / 0", ZERO / ZERO),
        ("Ω / Ω", OMEGA / OMEGA),
        ("ε / ε", EPSILON / EPSILON),
    ]
    for label, value in closure:
        print(f"  {label:>12}  →  {value}")


def _planck_example() -> None:
    """
    Physical interpretation: ε as Planck length.

    If ε ≡ ℓ_P ≈ 1.616×10⁻³⁵ m (smallest meaningful length),
    then Ω = 1/ε represents the number of Planck lengths per meter.
    """
    print("\n=== PLANCK SCALE INTERPRETATION ===\n")

    l_P = 1.616e-35  # Planck length in meters

    print(f"ε  ≡  ℓ_P  =  {l_P:.3e} m  (Planck length)")
    print(f"Ω  ≡  1/ℓ_P  =  {1/l_P:.3e}  (Planck lengths per meter)")

    print(f"\nKey identity: Ω · ε  →  {OMEGA * EPSILON}  (1 meter = 1 meter)")

    # Observable universe radius ≈ 4.4×10²⁶ m
    r_universe = 4.4e26
    n_planck = r_universe / l_P
    print(f"\nObservable universe radius: {r_universe:.1e} m")
    print(f"In Planck lengths: {n_planck:.2e} · ε")
    print(f"Symbolically: r · Ω · ε  =  r  (finite, no actual infinity)")

    # Ω² represents Planck areas per m²
    print(f"\nΩ²  ≡  Planck areas per m²  =  {(1/l_P)**2:.2e}")
    print(f"Symbolic derivation: Ω / ε  →  {OMEGA / EPSILON}")

    # The ε-continuum
    print(f"\n[0, 1]_ε  contains Ω points  ≈  {1/l_P:.2e} resolution elements")


if __name__ == "__main__":
    _test()
    _demo()
    _planck_example()
