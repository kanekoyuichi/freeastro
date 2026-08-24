from __future__ import annotations
import json

from ._utils.time import local_to_utc
from ._ephemeris.engine import get_planet_positions, build_planets
from ._ephemeris.houses import calculate_placidus_houses, build_houses
from .aspects import calculate_aspects
from .models import Planet, House, Aspect, ChartData


class AstrologicalSubject:
    """
    出生チャート計算のメインクラス。

    Args:
        name: 対象者の名前
        year, month, day: 出生日
        hour, minute: 出生時刻（ローカル時刻）
        latitude: 緯度（北緯正、南緯負）
        longitude: 経度（東経正、西経負）
        tz_str: タイムゾーン文字列（例: "Asia/Tokyo"）
    """

    def __init__(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        latitude: float,
        longitude: float,
        tz_str: str,
    ) -> None:
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.latitude = latitude
        self.longitude = longitude
        self.tz_str = tz_str

        self._utc_dt = local_to_utc(year, month, day, hour, minute, tz_str)
        self._computed = False

    def _ensure_computed(self) -> None:
        if self._computed:
            return
        cusps, asc, mc = calculate_placidus_houses(
            self._utc_dt, self.latitude, self.longitude
        )
        self._asc = asc
        self._mc = mc
        self._house_cusps = cusps
        self._houses = build_houses(cusps)

        raw = get_planet_positions(self._utc_dt, self.latitude, self.longitude)
        self._planets = build_planets(raw, cusps)
        self._planet_map = {p.name: p for p in self._planets}
        self._aspects = calculate_aspects(self._planets)
        self._computed = True

    # --- 惑星プロパティ ---

    @property
    def sun(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Sun"]

    @property
    def moon(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Moon"]

    @property
    def mercury(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Mercury"]

    @property
    def venus(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Venus"]

    @property
    def mars(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Mars"]

    @property
    def jupiter(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Jupiter"]

    @property
    def saturn(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Saturn"]

    @property
    def uranus(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Uranus"]

    @property
    def neptune(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Neptune"]

    @property
    def pluto(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["Pluto"]

    @property
    def true_node(self) -> Planet:
        self._ensure_computed()
        return self._planet_map["True Node"]

    @property
    def planets(self) -> list[Planet]:
        self._ensure_computed()
        return self._planets

    # --- ハウスプロパティ ---

    @property
    def houses(self) -> list[House]:
        self._ensure_computed()
        return self._houses

    @property
    def first_house(self) -> House:
        self._ensure_computed()
        return self._houses[0]

    @property
    def asc(self) -> float:
        self._ensure_computed()
        return self._asc

    @property
    def mc(self) -> float:
        self._ensure_computed()
        return self._mc

    # --- アスペクト ---

    @property
    def aspects(self) -> list[Aspect]:
        self._ensure_computed()
        return self._aspects

    # --- 出力 ---

    def to_dict(self) -> dict:
        self._ensure_computed()
        return ChartData(
            subject_name=self.name,
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            latitude=self.latitude,
            longitude=self.longitude,
            tz_str=self.tz_str,
            planets=self._planets,
            houses=self._houses,
            aspects=self._aspects,
            asc=self._asc,
            mc=self._mc,
        ).model_dump()

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def __repr__(self) -> str:
        return f"<AstrologicalSubject {self.name} {self.year}-{self.month:02d}-{self.day:02d}>"
