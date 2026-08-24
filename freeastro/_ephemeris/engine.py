from __future__ import annotations
import math
from datetime import datetime
from functools import lru_cache

import numpy as np
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


def _calc_true_node(jd_tt: float) -> float:
    """
    月の地心位置・速度の状態ベクトルから軌道面法線を求め、
    True Ascending Node の黄道経度（度）を算出する。
    精度 ≈ 0.001°（DE421 の精度に依存）。
    """
    planets = _get_planets()
    ts = _get_timescale()
    t = ts.tt_jd(jd_tt)

    geo_moon = (planets["moon"] - planets["earth"]).at(t)
    r = geo_moon.position.km
    v = geo_moon.velocity.km_per_s

    # 軌道面法線 h = r × v
    h = np.cross(r, v)

    # 黄道北極ベクトル (ICRS)
    rot = framelib.ecliptic_frame.rotation_at(t)
    ecl_north_icrs = rot.T @ np.array([0.0, 0.0, 1.0])

    # 昇交点方向 = ecl_north × h → 黄道座標に変換
    node_ecl = rot @ np.cross(ecl_north_icrs, h)

    return math.degrees(math.atan2(node_ecl[1], node_ecl[0])) % 360.0


@lru_cache(maxsize=128)
def _compute_planet_positions(jd_tt: float, latitude: float, longitude: float) -> dict[str, dict]:
    """
    キャッシュ付き惑星位置計算。同一 (JD, lat, lon) では再計算しない。
    """
    planets = _get_planets()
    ts = _get_timescale()
    t = ts.tt_jd(jd_tt)
    earth = planets["earth"]
    observer = earth + wgs84.latlon(latitude, longitude)

    # 逆行判定用: 前後2時間
    t_before = ts.tt_jd(jd_tt - 2 / 24)
    t_after = ts.tt_jd(jd_tt + 2 / 24)

    results: dict[str, dict] = {}

    for name in PLANET_NAMES:
        if name == "True Node":
            ecl_lon = _calc_true_node(jd_tt)
            # 月の昇交点は常に西向き（逆行）に移動する
            results[name] = {"longitude": ecl_lon, "retrograde": True}
            continue

        body_name = SKYFIELD_BODY_MAP[name]
        body = planets[body_name]

        astrometric = observer.at(t).observe(body).apparent()
        _, lon, _ = astrometric.frame_latlon(framelib.ecliptic_frame)
        ecl_lon = lon.degrees % 360.0

        # 逆行判定: 前後2時間の経度変化で判定
        a_before = observer.at(t_before).observe(body).apparent()
        a_after = observer.at(t_after).observe(body).apparent()
        _, lon_before, _ = a_before.frame_latlon(framelib.ecliptic_frame)
        _, lon_after, _ = a_after.frame_latlon(framelib.ecliptic_frame)
        delta = (lon_after.degrees - lon_before.degrees + 360.0) % 360.0
        retrograde = delta > 180.0

        results[name] = {"longitude": ecl_lon, "retrograde": retrograde}

    return results


def get_planet_positions(utc_dt: datetime, latitude: float, longitude: float) -> dict[str, dict]:
    """
    指定 UTC 日時・場所の全惑星の黄道経度・逆行フラグを計算して返す。
    戻り値: {惑星名: {"longitude": float, "retrograde": bool}}
    """
    ts = _get_timescale()
    t = ts.from_datetime(utc_dt)
    return _compute_planet_positions(t.tt, latitude, longitude)


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
        else:
            if lon >= cusp_start or lon < cusp_end:
                return i + 1
    return 1
