from __future__ import annotations
from .models import Planet, Aspect

# アスペクト名: (正確な角度, 許容誤差 orb)
ASPECTS: dict[str, tuple[float, float]] = {
    "Conjunction": (0.0, 8.0),
    "Opposition": (180.0, 8.0),
    "Trine": (120.0, 8.0),
    "Square": (90.0, 7.0),
    "Sextile": (60.0, 6.0),
}


def calculate_aspects(planets: list[Planet]) -> list[Aspect]:
    """全天体ペアのアスペクトを計算して返す"""
    result: list[Aspect] = []
    n = len(planets)
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = planets[i], planets[j]
            angle = _angular_distance(p1.position, p2.position)
            aspect = _find_aspect(angle)
            if aspect is not None:
                name, exact = aspect
                result.append(Aspect(
                    planet1=p1.name,
                    planet2=p2.name,
                    aspect=name,
                    angle=round(angle, 4),
                    orb=round(angle - exact, 4),
                ))
    return result


def _angular_distance(lon1: float, lon2: float) -> float:
    """2つの黄道経度の最小角度差を返す (0-180)"""
    diff = abs(lon1 - lon2) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def _find_aspect(angle: float) -> tuple[str, float] | None:
    """角度が許容誤差内のアスペクトを返す。なければ None"""
    for name, (exact, orb) in ASPECTS.items():
        if abs(angle - exact) <= orb:
            return name, exact
    return None
