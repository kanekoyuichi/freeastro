"""
freeastro vs kerykeion の精度比較テスト。
基準値は kerykeion 5.12.9 / pyswisseph DE431 から取得。
惑星: 0.1° 以内、Moon: 0.5° 以内、ハウス: 0.1° 以内 を許容。
"""
import json
import pytest
from freeastro import AstrologicalSubject


@pytest.fixture(scope="module")
def tokyo_1990():
    return AstrologicalSubject(
        name="Test Tokyo 1990",
        year=1990, month=1, day=15,
        hour=12, minute=0,
        latitude=35.6762, longitude=139.6503,
        tz_str="Asia/Tokyo",
    )


# ---- 惑星位置 ---- #

def test_sun_position(tokyo_1990):
    assert abs(tokyo_1990.sun.position - 294.6964) < 0.1

def test_sun_sign(tokyo_1990):
    assert tokyo_1990.sun.sign == "Capricorn"

def test_sun_not_retrograde(tokyo_1990):
    assert tokyo_1990.sun.retrograde is False

def test_moon_position(tokyo_1990):
    # エフェメリス版差（DE421 vs DE431）で 0.5° 許容
    assert abs(tokyo_1990.moon.position - 162.7957) < 0.5

def test_moon_sign(tokyo_1990):
    assert tokyo_1990.moon.sign == "Virgo"

def test_mercury_retrograde(tokyo_1990):
    assert tokyo_1990.mercury.retrograde is True

def test_venus_retrograde(tokyo_1990):
    assert tokyo_1990.venus.retrograde is True

def test_venus_position(tokyo_1990):
    assert abs(tokyo_1990.venus.position - 300.9074) < 0.1

def test_mercury_position(tokyo_1990):
    assert abs(tokyo_1990.mercury.position - 281.6256) < 0.1

def test_mars_position(tokyo_1990):
    assert abs(tokyo_1990.mars.position - 259.6422) < 0.1

def test_mars_not_retrograde(tokyo_1990):
    assert tokyo_1990.mars.retrograde is False


# ---- True Node ---- #

def test_true_node_position(tokyo_1990):
    # kerykeion 基準: 316.5697°（状態ベクトル法で 0.01° 以内）
    assert abs(tokyo_1990.true_node.position - 316.5697) < 0.1

def test_true_node_sign(tokyo_1990):
    assert tokyo_1990.true_node.sign == "Aquarius"

def test_true_node_retrograde(tokyo_1990):
    # 月の昇交点は常に逆行
    assert tokyo_1990.true_node.retrograde is True


# ---- ハウスカスプ ---- #

KERYKEION_HOUSES = {
    1: 43.1160, 2: 71.8364, 3: 94.5725, 4: 116.9172,
    5: 143.2461, 6: 178.5688, 7: 223.1160, 8: 251.8364,
    9: 274.5725, 10: 296.9172, 11: 323.2461, 12: 358.5688,
}

@pytest.mark.parametrize("house_num,expected", KERYKEION_HOUSES.items())
def test_house_cusp(tokyo_1990, house_num, expected):
    h = tokyo_1990.houses[house_num - 1]
    assert abs(h.position - expected) < 0.1, (
        f"H{house_num}: freeastro={h.position:.4f}° expected={expected:.4f}°"
    )

def test_asc(tokyo_1990):
    assert abs(tokyo_1990.asc - 43.1160) < 0.1

def test_mc(tokyo_1990):
    assert abs(tokyo_1990.mc - 296.9172) < 0.1

def test_first_house_sign(tokyo_1990):
    assert tokyo_1990.first_house.sign == "Taurus"


# ---- ハウス帰属 ---- #

def test_sun_house(tokyo_1990):
    assert tokyo_1990.sun.house == 9

def test_moon_house(tokyo_1990):
    assert tokyo_1990.moon.house == 5

def test_venus_house(tokyo_1990):
    assert tokyo_1990.venus.house == 10


# ---- 全天体リスト ---- #

def test_planets_count(tokyo_1990):
    assert len(tokyo_1990.planets) == 11  # True Node を含む

def test_planet_names(tokyo_1990):
    names = [p.name for p in tokyo_1990.planets]
    for expected in ["Sun", "Moon", "Mercury", "Venus", "Mars",
                     "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "True Node"]:
        assert expected in names


# ---- アスペクト ---- #

def test_aspects_exist(tokyo_1990):
    assert len(tokyo_1990.aspects) > 0

def test_aspect_fields(tokyo_1990):
    a = tokyo_1990.aspects[0]
    assert isinstance(a.planet1, str)
    assert isinstance(a.planet2, str)
    assert isinstance(a.aspect, str)
    assert 0.0 <= a.angle <= 180.0
    assert a.aspect in ("Conjunction", "Opposition", "Trine", "Square", "Sextile")

def test_sun_venus_conjunction(tokyo_1990):
    # 太陽(294.7°) と金星(300.9°) は約 6.2° 差 → Conjunction
    aspects = [a for a in tokyo_1990.aspects
               if set([a.planet1, a.planet2]) == {"Sun", "Venus"}]
    assert len(aspects) == 1
    assert aspects[0].aspect == "Conjunction"
    assert abs(aspects[0].orb) < 8.0

def test_aspect_orb_within_limit(tokyo_1990):
    orb_limits = {"Conjunction": 8, "Opposition": 8, "Trine": 8, "Square": 7, "Sextile": 6}
    for a in tokyo_1990.aspects:
        assert abs(a.orb) <= orb_limits[a.aspect], (
            f"{a.planet1} {a.aspect} {a.planet2}: orb={a.orb:.2f}° exceeds limit"
        )


# ---- JSON 出力 ---- #

def test_to_dict(tokyo_1990):
    d = tokyo_1990.to_dict()
    assert d["subject_name"] == "Test Tokyo 1990"
    assert len(d["planets"]) == 11
    assert len(d["houses"]) == 12
    assert "aspects" in d
    assert "asc" in d
    assert "mc" in d

def test_to_json(tokyo_1990):
    j = tokyo_1990.to_json()
    parsed = json.loads(j)
    assert parsed["subject_name"] == "Test Tokyo 1990"
    assert "aspects" in parsed

def test_repr(tokyo_1990):
    assert "Test Tokyo 1990" in repr(tokyo_1990)
    assert "1990" in repr(tokyo_1990)
