from __future__ import annotations
import math
from datetime import datetime
from functools import lru_cache

from skyfield.api import load
from skyfield import framelib

from ..constants import longitude_to_sign
from ..models import House


def _get_timescale():
    return load.timescale()


def _get_obliquity(t) -> float:
    """黄道傾斜角（ラジアン）を返す"""
    matrix = framelib.ecliptic_frame.rotation_at(t)
    return abs(math.asin(matrix[1][2]))


def _greenwich_sidereal_time(t) -> float:
    """グリニッジ恒星時（度）を返す"""
    return t.gast * 15.0


def _ra_to_ecliptic_lon(ra_rad: float, eps: float) -> float:
    """
    赤経（ラジアン）→ 黄道経度（ラジアン）。
    黄道上の点を仮定した直接変換式: tan(L) = tan(RA) / cos(ε)
    """
    lon = math.atan2(math.sin(ra_rad), math.cos(ra_rad) * math.cos(eps))
    return lon % (2 * math.pi)


def _calc_mc(ramc: float, eps: float) -> float:
    """MC の黄道経度（度）を算出"""
    mc = math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps))
    mc_deg = math.degrees(mc) % 360.0
    ramc_deg = math.degrees(ramc) % 360.0
    if ramc_deg >= 180.0 and mc_deg < 180.0:
        mc_deg += 180.0
    elif ramc_deg < 180.0 and mc_deg >= 180.0:
        mc_deg -= 180.0
    return mc_deg % 360.0


def _calc_asc(ramc: float, lat: float, eps: float) -> float:
    """ASC の黄道経度（度）を算出"""
    denom = math.sin(ramc) * math.cos(eps) + math.tan(lat) * math.sin(eps)
    asc = math.atan2(-math.cos(ramc), denom)
    asc_deg = math.degrees(asc) % 360.0
    mc_deg = _calc_mc(ramc, eps)
    if asc_deg < mc_deg:
        asc_deg += 180.0
    return asc_deg % 360.0


def _calc_intermediate_cusp(
    ramc: float,
    lat: float,
    eps: float,
    fraction: float,
    upper: bool,
) -> float:
    """
    Placidus 中間ハウスカスプを反復法で計算する。

    upper=True:  MC→ASC 方向（H11=1/3, H12=2/3）
    upper=False: ASC→IC 方向（H2=1/3, H3=2/3）
    """
    TAU = 2 * math.pi

    if upper:
        initial_ra = (ramc + math.radians(fraction * 90.0)) % TAU
    else:
        initial_ra = (ramc + math.pi + math.radians(fraction * 90.0)) % TAU

    lon = _ra_to_ecliptic_lon(initial_ra, eps)

    for _ in range(100):
        dec = math.asin(math.sin(eps) * math.sin(lon))
        cos_ha = -math.tan(lat) * math.tan(dec)

        if abs(cos_ha) > 1.0:
            return math.degrees(lon) % 360.0

        sd = math.acos(max(-1.0, min(1.0, cos_ha)))

        if upper:
            target_ra = (ramc + fraction * sd) % TAU
        else:
            na = math.pi - sd
            target_ra = (ramc + math.pi - (1.0 - fraction) * na) % TAU

        new_lon = _ra_to_ecliptic_lon(target_ra, eps)

        if abs(new_lon - lon) < 1e-7:
            lon = new_lon
            break
        lon = new_lon

    return math.degrees(lon) % 360.0


@lru_cache(maxsize=128)
def _compute_placidus_houses(
    jd_tt: float,
    latitude: float,
    longitude: float,
) -> tuple[tuple[float, ...], float, float]:
    """
    キャッシュ付き Placidus ハウス計算。
    戻り値はタプル（lru_cache のため hashable にする）。
    """
    ts = _get_timescale()
    t = ts.tt_jd(jd_tt)

    eps = _get_obliquity(t)
    gst = _greenwich_sidereal_time(t)
    lst = (gst + longitude) % 360.0
    ramc = math.radians(lst)
    lat = math.radians(latitude)

    mc_lon = _calc_mc(ramc, eps)
    asc_lon = _calc_asc(ramc, lat, eps)
    ic_lon = (mc_lon + 180.0) % 360.0
    desc_lon = (asc_lon + 180.0) % 360.0

    h11 = _calc_intermediate_cusp(ramc, lat, eps, 1.0 / 3.0, upper=True)
    h12 = _calc_intermediate_cusp(ramc, lat, eps, 2.0 / 3.0, upper=True)
    h2 = _calc_intermediate_cusp(ramc, lat, eps, 1.0 / 3.0, upper=False)
    h3 = _calc_intermediate_cusp(ramc, lat, eps, 2.0 / 3.0, upper=False)

    cusps = (
        asc_lon,                    # H1
        h2,                         # H2
        h3,                         # H3
        ic_lon,                     # H4
        (h11 + 180.0) % 360.0,     # H5
        (h12 + 180.0) % 360.0,     # H6
        desc_lon,                   # H7
        (h2 + 180.0) % 360.0,      # H8
        (h3 + 180.0) % 360.0,      # H9
        mc_lon,                     # H10
        h11,                        # H11
        h12,                        # H12
    )
    return cusps, asc_lon, mc_lon


def calculate_placidus_houses(
    utc_dt: datetime,
    latitude: float,
    longitude: float,
) -> tuple[list[float], float, float]:
    """
    Placidus ハウスカスプを計算する。
    戻り値: (cusps[0..11], asc, mc) — cusps[0]=H1カスプ, cusps[9]=H10(MC)
    """
    ts = _get_timescale()
    t = ts.from_datetime(utc_dt)
    cusps_tuple, asc, mc = _compute_placidus_houses(t.tt, latitude, longitude)
    return list(cusps_tuple), asc, mc


def build_houses(cusps: list[float]) -> list[House]:
    """カスプリストから House モデルのリストを構築する"""
    houses: list[House] = []
    for i, cusp in enumerate(cusps):
        sign, sign_deg = longitude_to_sign(cusp)
        houses.append(House(
            number=i + 1,
            sign=sign,
            position=cusp,
            sign_degree=sign_deg,
        ))
    return houses
