BeginSet
===

俺式アプリ準備セット。カレントディレクトリを import した場所に移す。さらにカレント以下のディレクトリをすべてインポートパスに追加し、相対インポートを不要にします。

- Docker: 対応!
- Python: 3.14!
- Linter: ruff!
- Test: pytest!

## パッと実行してみたい

```bash
docker compose run --rm --build app
```

ruff の lint とフォーマットチェック、pytest のテストが走ります。

```bash
docker compose run --rm --build app python begin_set.py
```

begin_set.py を直接実行したときのテスト動作です。コンテナ内の /app で、カレントの移動先と、インポートパスに追加されるディレクトリ一覧を表示します。

## Description

- カレント移して
- カレント以下のディレクトリを取得して
- 全部インポートパスに登録しますよ。

## Usage

```python
import begin_set

begin_set.exec_all(__file__)
```

begin_set.py を直接実行しても、テスト動作で動きます。

## 開発

- 依存ライブラリは開発用だけです (requirements-dev.txt)。begin_set.py 自体は標準ライブラリのみで動きます。
- CI (GitHub Actions) で ruff, pytest, pip-audit を回します。
