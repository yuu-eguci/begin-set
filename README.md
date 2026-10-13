BeginSet
===

俺式アプリ準備セット。
スクリプトのある場所へ移動して、配下のフォルダを import の検索先に追加するやつ。

- Docker: 対応!
- Python: 3.14!
- Linter: ruff!
- Test: pytest!

## パッと実行してみたい

```bash
docker compose run --rm --build app python begin_set.py
```

これでコンテナ内のデモが動く。
移動先と import の検索先が表示されるので、まずは見てみてどうぞ。

細かいとこ:

- 標準設定では `__pycache__` や `.git`、`.venv` は入れない。
- 読めないフォルダの中は飛ばす。
- リンクは配下を指すものだけたどる。同じ実体は 1 回だけ。
- 何回呼んでも、同じパスは増やさない。
- 相対パスでも OK。

## 注意

検索先の先頭に追加するので、配下に `json.py` があれば標準ライブラリより優先される。
他人が書き込めるフォルダ (アップロード先とか) がある場所では使わないでね。
標準ライブラリと同じ名前の `.py` やパッケージを見つけたら、`UserWarning` で知らせる。

## Usage

```python
import begin_set

begin_set.exec_all(__file__)
```

## 開発

```bash
docker compose run --rm --build app
```

lint とテストはこれで。
GitHub Actions では脆弱性チェックも回す。
`begin_set.py` 自体は標準ライブラリだけで動くよ。
