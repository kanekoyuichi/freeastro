from __future__ import annotations

SIGNS: list[str] = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANET_NAMES: list[str] = [
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
    "True Node",
]

# skyfield の惑星名マッピング
SKYFIELD_BODY_MAP: dict[str, str] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter",
}


def longitude_to_sign(longitude: float) -> tuple[str, float]:
    """黄道経度 (0-360) から星座名と星座内度数を返す"""
    lon = longitude % 360.0
    index = int(lon / 30)
    degree = lon - index * 30.0
    return SIGNS[index], degree
