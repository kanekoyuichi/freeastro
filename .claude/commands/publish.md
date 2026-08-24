# publish — PyPI へリリース

バージョンを上げて PyPI に公開する。GitHub Actions の publish.yml が tag push をトリガーに実行される。

## 前提条件

- GitHub リポジトリの Secrets に `PYPI_API_TOKEN` が登録済みであること
  - PyPI → Account settings → API tokens でトークンを発行
  - GitHub → Settings → Secrets → Actions → New repository secret で `PYPI_API_TOKEN` として登録

## 手順

### 1. 現在のバージョンを確認

`pyproject.toml` の `version` フィールドを読み取り、ユーザーに提示する。

### 2. 新しいバージョンを決める

セマンティックバージョニング（`MAJOR.MINOR.PATCH`）に従い、変更内容に応じて提案する：

- **PATCH**（`0.1.0` → `0.1.1`）: バグ修正のみ
- **MINOR**（`0.1.0` → `0.2.0`）: 後方互換の新機能追加
- **MAJOR**（`0.1.0` → `1.0.0`）: 後方互換性のない変更

ユーザーに確認を取ってから進める。

### 3. pyproject.toml のバージョンを更新

`version = "X.Y.Z"` の行を新しいバージョンに書き換える。

### 4. コミット・タグ・プッシュ

```bash
git add pyproject.toml
git commit -m "Bump version to vX.Y.Z"
git tag vX.Y.Z
git push origin main
git push origin vX.Y.Z
```

tag の push が GitHub Actions の `publish.yml` をトリガーし、自動的に PyPI へ公開される。

### 5. 完了確認

- GitHub Actions の実行状況を `gh run list --limit 3` で確認する
- PyPI の公開完了後、`pip install freeastro==X.Y.Z` で動作を確認する
