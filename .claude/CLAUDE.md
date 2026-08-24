# freeastro — Claude 作業ルール

## プロジェクト概要

MIT ライセンスの Python 占星術ライブラリ。ネイタルチャート（出生図）を計算する。

- 計算エンジン: Skyfield (DE421) + 独自 Placidus 実装
- データモデル: Pydantic v2
- Python 3.10+

## リリースフロー

**PyPI への公開は必ず `/publish` スキル経由で行う。**

1. `pyproject.toml` のバージョンを上げる
2. `git tag vX.Y.Z` を push する
3. GitHub Actions (`publish.yml`) が自動的にビルド・PyPI 公開する

直接 `pip publish` や `twine upload` は使わない。

## コード規約

- 依存ライブラリを増やす前に確認を取る（Pure Python 方針を維持）
- 計算精度の変更は必ずテストで kerykeion 基準値との比較を行う
- 公開 API（`AstrologicalSubject` のプロパティ名）は後方互換を維持する

## テスト

```bash
python -m pytest tests/ -v
```

34テストが全て通ることを確認してからコミットする。
