
BeginSet
===

俺式アプリ準備セット。カレントディレクトリを import した場所に移す。さらにカレント以下のディレクトリをすべてインポートパスに追加し、相対インポートを不要にします。

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
