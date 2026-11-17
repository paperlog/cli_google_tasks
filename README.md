# CLI google tasks

cli上でgoogleタスクを操作する。

## 使い方

### 基本構文
1. タスクの一覧表示（引数なし）
`python main.py`

2. 通常のタスク追加
`python main.py <タイトル> <m/d,h,m(日時)> <説明>`

3. テンプレートタスクの追加
`python main.py -<設定したショートカット名>`
