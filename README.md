# CLI google tasks

cli上でgoogleタスクを操作する。

## 使い方

### google tasks api利用準備
- [credentials.jsonをダウンロード](https://developers.google.com/workspace/tasks/quickstart/python?hl=ja)してmain.pyと同階層に配置する。

### ショートカット

実行した日以降の指定した曜日の日付を自動計算し、テンプレートのタスクを追加します。

#### ショートカットの編集(shortcut.json)
```json
{
    "-<任意の文字>" :{
	"title" : "タイトル",
	"due" : {
	    "day" : "「月」や「金」など特定の曜日を一字 例：月",
	    "time" : "締め切り時間 例：23:59"
	},
	"notes" : "タスクの追加説明 / 空文字" 
    }
}
```

### 基本構文
1. タスクの一覧表示
- `python main.py`
- `python main.py -c` 通信せずローカルファイル閲覧

2. 通常のタスク追加のパターン
- `python main.py <タイトル> <m/d,h:m(例：01:20,09:00)> <説明>`
- `python main.py <タイトル>`
- `python main.py <タイトル> <m/d,h:m(例: 12:02,23:59)>`
- `python main.py <タイトル> <説明>`

3. テンプレートタスクの追加
- `python main.py -<設定したショートカット名>`
