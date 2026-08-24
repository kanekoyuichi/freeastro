# freeastro

A free Python library that calculates astrological birth charts (natal charts).

**Good for:**
- Building horoscope or astrology apps
- Automating birth chart generation for multiple people
- Adding astrology features to an existing web service
- Learning astrology calculations programmatically

Give it a birth date, time, and place — get back the positions of planets and house cusps as Python objects or JSON.

## Install

```bash
pip install freeastro
```

> The first time you run freeastro, it automatically downloads a ~17 MB planetary data file (NASA DE421 ephemeris). After that, everything works offline.

## Usage

### Step 1 — Create a subject

Pass the birth data of the person you want to calculate a chart for:

```python
from freeastro import AstrologicalSubject

subject = AstrologicalSubject(
    name="John Doe",
    year=1990,
    month=1,
    day=15,
    hour=12,      # 24-hour format, local time
    minute=0,
    latitude=35.6762,    # Tokyo: positive = North
    longitude=139.6503,  # Tokyo: positive = East
    tz_str="Asia/Tokyo", # timezone string
)
```

**How to find latitude, longitude, and timezone**

| City | latitude | longitude | tz_str |
|------|----------|-----------|--------|
| Tokyo | 35.6762 | 139.6503 | `"Asia/Tokyo"` |
| New York | 40.7128 | -74.0060 | `"America/New_York"` |
| London | 51.5074 | -0.1278 | `"Europe/London"` |
| Paris | 48.8566 | 2.3522 | `"Europe/Paris"` |
| Sydney | -33.8688 | 151.2093 | `"Australia/Sydney"` |

For other cities, right-click on Google Maps to get coordinates. Find the timezone string on [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

**Notes on signs:**
- South latitudes are **negative** (e.g. Sydney: `-33.8688`)
- West longitudes are **negative** (e.g. New York: `-74.0060`)

### Step 2 — Read planet positions

```python
# Sun sign and degree
print(subject.sun.sign)         # "Capricorn"
print(subject.sun.sign_degree)  # 24.70  (degrees within that sign)
print(subject.sun.house)        # 9      (which house the Sun is in)

# Check if a planet is retrograde
print(subject.mercury.retrograde)  # True

# Available planets
print(subject.moon)
print(subject.mercury)
print(subject.venus)
print(subject.mars)
print(subject.jupiter)
print(subject.saturn)
print(subject.uranus)
print(subject.neptune)
print(subject.pluto)
print(subject.true_node)  # Moon's True North Node
```

### Step 3 — Read aspects

Aspects describe angular relationships between planets (e.g. a trine, a square).

```python
# All aspects in the chart
for aspect in subject.aspects:
    print(aspect)
# <Aspect Moon Trine Mercury (orb -0.91°)>
# <Aspect Sun Conjunction Venus (orb +6.21°)>
# ...

# Filter by type
trines = [a for a in subject.aspects if a.aspect == "Trine"]

# Check a specific pair
sun_moon = [a for a in subject.aspects
            if {a.planet1, a.planet2} == {"Sun", "Moon"}]
```

Supported aspects: Conjunction (0°), Opposition (180°), Trine (120°), Square (90°), Sextile (60°).

### Step 4 — Read house cusps

```python
# Ascendant (1st house cusp)
print(subject.first_house.sign)  # "Taurus"

# Midheaven (10th house cusp) as ecliptic longitude
print(subject.mc)   # 296.92

# All 12 houses
for house in subject.houses:
    print(f"House {house.number}: {house.sign} {house.sign_degree:.1f}°")
```

### Step 5 — Export the data

```python
# As a Python dict
data = subject.to_dict()

# As a JSON string (pretty-printed)
json_str = subject.to_json()
print(json_str)
```

Example JSON output (excerpt):

```json
{
  "subject_name": "John Doe",
  "year": 1990,
  "month": 1,
  "day": 15,
  "planets": [
    {
      "name": "Sun",
      "sign": "Capricorn",
      "position": 294.70,
      "sign_degree": 24.70,
      "house": 9,
      "retrograde": false
    }
  ],
  "asc": 43.12,
  "mc": 296.92
}
```

## Data fields

### Planet

| Field | Example | Meaning |
|-------|---------|---------|
| `name` | `"Sun"` | Planet name |
| `sign` | `"Capricorn"` | Zodiac sign the planet is in |
| `sign_degree` | `24.70` | Degrees within that sign (0–30) |
| `position` | `294.70` | Absolute ecliptic longitude (0–360) |
| `house` | `9` | House number (1–12) |
| `retrograde` | `False` | Whether the planet appears to move backward |

### House

| Field | Example | Meaning |
|-------|---------|---------|
| `number` | `1` | House number (1–12) |
| `sign` | `"Taurus"` | Zodiac sign of the house cusp |
| `sign_degree` | `13.12` | Degrees within that sign (0–30) |
| `position` | `43.12` | Absolute ecliptic longitude (0–360) |

### Aspect

| Field | Example | Meaning |
|-------|---------|---------|
| `planet1` | `"Sun"` | First planet |
| `planet2` | `"Venus"` | Second planet |
| `aspect` | `"Conjunction"` | Aspect type |
| `angle` | `6.21` | Actual angular distance between planets (0–180) |
| `orb` | `6.21` | Deviation from the exact aspect angle |

## Troubleshooting

**The download hangs or fails on first run**
freeastro downloads a ~17 MB file from a NASA server. If it fails, check your internet connection and try running again. The file is cached after the first successful download.

**I get a `ZoneInfoNotFoundError` for my timezone**
The `tz_str` value must be an exact match from the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). Common mistakes: `"JST"` should be `"Asia/Tokyo"`, `"EST"` should be `"America/New_York"`.

**The planet positions look off**
Double-check that:
- `hour` and `minute` are in **local time**, not UTC
- South latitudes are negative (e.g. `-33.86` for Sydney)
- West longitudes are negative (e.g. `-74.00` for New York)

**`ModuleNotFoundError: No module named 'freeastro'`**
Run `pip install freeastro` first. If you're using a virtual environment, make sure it's activated.

## Requirements

- Python 3.10 or later
- Internet connection on first run (to download the ephemeris)

## License

MIT — free to use for any purpose, including commercial projects.
