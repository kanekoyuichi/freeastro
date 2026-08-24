# freeastro

占星術のネイタルチャート（出生図）を計算する、無料の Python ライブラリです。

**こんな用途に使えます：**
- 星占いアプリや占星術サービスを作りたい
- 大量の人の出生図を自動生成したい
- 既存の Web サービスに占星術機能を追加したい
- 占星術の計算をプログラムで学びたい

生年月日・出生時刻・出生地を渡すと、惑星の位置やハウスカスプを Python オブジェクトまたは JSON で取得できます。

## インストール

```bash
pip install freeastro
```

> 初回実行時に、惑星データファイル（NASA DE421、約 17 MB）を自動でダウンロードします。2回目以降はオフラインで動作します。

## 使い方

### ステップ 1 — チャートを作成する

計算したい人の出生データを渡します。

```python
from freeastro import AstrologicalSubject

subject = AstrologicalSubject(
    name="山田太郎",
    year=1990,
    month=1,
    day=15,
    hour=12,   # 24時間表記、現地時刻
    minute=0,
    latitude=35.6762,    # 東京: 北緯は正の値
    longitude=139.6503,  # 東京: 東経は正の値
    tz_str="Asia/Tokyo", # タイムゾーン文字列
)
```

**主要都市の緯度・経度・タイムゾーン**

| 都市 | latitude | longitude | tz_str |
|------|----------|-----------|--------|
| 東京 | 35.6762 | 139.6503 | `"Asia/Tokyo"` |
| 大阪 | 34.6937 | 135.5023 | `"Asia/Tokyo"` |
| ニューヨーク | 40.7128 | -74.0060 | `"America/New_York"` |
| ロンドン | 51.5074 | -0.1278 | `"Europe/London"` |
| パリ | 48.8566 | 2.3522 | `"Europe/Paris"` |
| シドニー | -33.8688 | 151.2093 | `"Australia/Sydney"` |

その他の都市は、Google マップで場所を右クリックすると緯度・経度を確認できます。タイムゾーン文字列は [こちらのリスト](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) を参照してください。

**符号（プラス・マイナス）について：**
- 南緯は**マイナス**（例：シドニー `-33.8688`）
- 西経は**マイナス**（例：ニューヨーク `-74.0060`）

### ステップ 2 — 惑星の位置を読み取る

```python
# 太陽の星座と度数
print(subject.sun.sign)         # "Capricorn"（山羊座）
print(subject.sun.sign_degree)  # 24.70（星座内の度数）
print(subject.sun.house)        # 9（何ハウスにあるか）

# 逆行しているか確認
print(subject.mercury.retrograde)  # True

# 取得できる天体
print(subject.moon)     # 月
print(subject.mercury)  # 水星
print(subject.venus)    # 金星
print(subject.mars)     # 火星
print(subject.jupiter)  # 木星
print(subject.saturn)   # 土星
print(subject.uranus)   # 天王星
print(subject.neptune)  # 海王星
print(subject.pluto)    # 冥王星
```

**星座名は英語で返ってきます。** 日本語表記が必要な場合は、以下の対応表を参考にしてください。

| 返り値 | 日本語 | 返り値 | 日本語 |
|--------|--------|--------|--------|
| `Aries` | 牡羊座 | `Libra` | 天秤座 |
| `Taurus` | 牡牛座 | `Scorpio` | 蠍座 |
| `Gemini` | 双子座 | `Sagittarius` | 射手座 |
| `Cancer` | 蟹座 | `Capricorn` | 山羊座 |
| `Leo` | 獅子座 | `Aquarius` | 水瓶座 |
| `Virgo` | 乙女座 | `Pisces` | 魚座 |

### ステップ 3 — ハウスカスプを読み取る

```python
# アセンダント（第1ハウスのカスプ）
print(subject.first_house.sign)  # "Taurus"（牡牛座）

# MC（天頂）の黄道経度
print(subject.mc)   # 296.92

# 全12ハウスの一覧
for house in subject.houses:
    print(f"第{house.number}ハウス: {house.sign} {house.sign_degree:.1f}°")
```

### ステップ 4 — データをエクスポートする

```python
# Python の dict として取得
data = subject.to_dict()

# JSON 文字列として取得
json_str = subject.to_json()
print(json_str)
```

JSON 出力の例（抜粋）：

```json
{
  "subject_name": "山田太郎",
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

## データの項目

### Planet（惑星）

| フィールド | 例 | 意味 |
|-----------|-----|------|
| `name` | `"Sun"` | 天体名 |
| `sign` | `"Capricorn"` | 位置している星座（英語名） |
| `sign_degree` | `24.70` | 星座内の度数（0〜30） |
| `position` | `294.70` | 黄道経度（0〜360の絶対値） |
| `house` | `9` | ハウス番号（1〜12） |
| `retrograde` | `False` | 逆行中かどうか |

### House（ハウス）

| フィールド | 例 | 意味 |
|-----------|-----|------|
| `number` | `1` | ハウス番号（1〜12） |
| `sign` | `"Taurus"` | カスプの星座（英語名） |
| `sign_degree` | `13.12` | 星座内の度数（0〜30） |
| `position` | `43.12` | 黄道経度（0〜360の絶対値） |

## うまく動かないときは

**初回起動時にダウンロードが止まる・失敗する**
インターネット接続を確認してから、もう一度実行してください。ダウンロードが完了すれば次回以降はオフラインで動きます。

**`ZoneInfoNotFoundError` というエラーが出る**
`tz_str` の値が正しくありません。`"JST"` ではなく `"Asia/Tokyo"`、`"EST"` ではなく `"America/New_York"` のように、[tz データベース](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) に掲載されている形式で指定してください。

**惑星の位置がおかしい**
以下を確認してください：
- `hour` と `minute` は **現地時刻**（UTC ではない）で指定しているか
- 南緯はマイナス（例：シドニー `-33.86`）になっているか
- 西経はマイナス（例：ニューヨーク `-74.00`）になっているか

**`ModuleNotFoundError: No module named 'freeastro'` と出る**
`pip install freeastro` を先に実行してください。仮想環境を使っている場合は、その環境が有効になっているか確認してください。

## 動作環境

- Python 3.10 以上
- 初回実行時のみインターネット接続が必要（エフェメリスのダウンロード）

## ライセンス

MIT — 商用利用を含む、あらゆる用途に無償で利用できます。
