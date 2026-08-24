from __future__ import annotations
from pydantic import BaseModel
import json


class Planet(BaseModel):
    name: str
    sign: str
    position: float        # 黄道経度 0-360
    sign_degree: float     # 星座内度数 0-30
    house: int
    retrograde: bool

    def __repr__(self) -> str:
        retro = " ℞" if self.retrograde else ""
        return f"<Planet {self.name}: {self.sign} {self.sign_degree:.2f}°{retro} H{self.house}>"


class House(BaseModel):
    number: int            # 1-12
    sign: str
    position: float        # カスプの黄道経度 0-360
    sign_degree: float     # 星座内度数 0-30

    def __repr__(self) -> str:
        return f"<House {self.number}: {self.sign} {self.sign_degree:.2f}°>"


class Aspect(BaseModel):
    planet1: str
    planet2: str
    aspect: str            # "Conjunction", "Opposition" etc.
    angle: float           # 実際の角度差 (0-180)
    orb: float             # 正確な角度からのずれ

    def __repr__(self) -> str:
        return f"<Aspect {self.planet1} {self.aspect} {self.planet2} (orb {self.orb:+.2f}°)>"


class ChartData(BaseModel):
    subject_name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    tz_str: str
    planets: list[Planet]
    houses: list[House]
    aspects: list[Aspect]
    asc: float
    mc: float
