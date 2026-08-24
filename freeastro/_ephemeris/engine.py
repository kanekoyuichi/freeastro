from __future__ import annotations
import math
from datetime import datetime
from functools import lru_cache

from skyfield.api import load, wgs84
from skyfield import framelib

from ..constants import SKYFIELD_BODY_MAP, PLANET_NAMES, longitude_to_sign
from ..models import Planet


@lru_cache(maxsize=1)
def _get_planets():
    """DE421 エフェメリスをロード（初回のみ）"""
    return load("de421.bsp")


@lru_cache(maxsize=1)
def _get_timescale():
    return load.timescale()


def get_planet_positions(utc_dt: datetime, latitude: float, longitude: float) -> dict[str, dict]:
    """
    指定 UTC 日時・場所の全惑星の黄道経度・逆行フラグを計算して返す。
    戻り値: {惑星名: {"longitude": float, "retrograde": bool}}
    """
    planets = _get_planets()
    ts = _get_timescale()

    t = ts.from_datetime(utc_dt)
    earth = planets["earth"]
    observer = earth + wgs84.latlon(latitude, longitude)

    results: dict[str, dict] = {}

    for name in PLANET_NAMES:
        body_name = SKYFIELD_BODY_MAP[name]
        body = planets[body_name]

        # 地心黄道座標（真黄道 of date）
        astrometric = observer.at(t).observe(body).apparent()
        lat, lon, _ = astrometric.frame_latlon(framelib.ecliptic_frame)
        ecl_lon = lon.degrees % 360.0

        # 逆行判定: わずか後の時刻と比較して経度が減少していれば逆行
        t2 = ts.tt_jd(t.tt + 1.0)
        astrometric2 = observer.at(t2).observe(body).apparent()
        _, lon2, _ = astrometric2.frame_latlon(framelib.ecliptic_frame)
        delta = (lon2.degrees - lon.degrees + 360.0) % 360.0
        retrograde = delta > 180.0  # 差が180°超 = 逆行

        results[name] = {"longitude": ecl_lon, "retrograde": retrograde}

    return results


def build_planets(
    raw: dict[str, dict],
    house_cusps: list[float],
) -> list[Planet]:
    """生データから Planet モデルのリストを構築する"""
    planet_list: list[Planet] = []
    for name in PLANET_NAMES:
        d = raw[name]
        lon = d["longitude"]
        sign, sign_deg = longitude_to_sign(lon)
        house = _assign_house(lon, house_cusps)
        planet_list.append(Planet(
            name=name,
            sign=sign,
            position=lon,
            sign_degree=sign_deg,
            house=house,
            retrograde=d["retrograde"],
        ))
    return planet_list


def _assign_house(longitude: float, cusps: list[float]) -> int:
    """惑星の黄道経度がどのハウスに属するか判定する（1-indexed）"""
    lon = longitude % 360.0
    n = len(cusps)
    for i in range(n):
        cusp_start = cusps[i] % 360.0
        cusp_end = cusps[(i + 1) % n] % 360.0
        if cusp_start <= cusp_end:
            if cusp_start <= lon < cusp_end:
                return i + 1
        else:  # カスプが 360° をまたぐ場合
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 1
