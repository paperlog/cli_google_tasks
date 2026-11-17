# CLI\_GOOGLE\_TASKS設計メモ

## 1. ゴール（何を作るか・やらないこと）
- **作るもの**：google_tasksのタスクの確認、追加をcliから行えるアプリ。課題管理ようにショートカットも。
- **やらないこと**：DBはjsonで代用。タスクの削除もいらない。

## 2. 扱うデータ（概念モデル）
- **tasklists**:[by google](https://developers.google.com/workspace/tasks/reference/rest/v1/tasklists?hl=ja&_gl=1*1vgg4fg*_up*MQ..*_ga*MTQ1MjMzMDM5MS4xNzk0ODk0OTQ1*_ga_SM8HXJ53K2*czE3OTQ4OTQ5NDQkbzEkZzAkdDE3OTQ4OTQ5NDQkajYwJGwwJGgw)
- **tasks**: [by google](https://developers.google.com/workspace/tasks/reference/rest/v1/tasks?hl=ja&_gl=1*pplhq4*_up*MQ..*_ga*MTQ1MjMzMDM5MS4xNzk0ODk0OTQ1*_ga_SM8HXJ53K2*czE3OTQ4OTQ5NDQkbzEkZzAkdDE3OTQ4OTQ5NDQkajYwJGwwJGgw)

## 3. コアロジック（やることリスト）
1. gooletasksのapi使ってデータのロード、繋がらない場合はローカルjson参照
2. タスク一覧表示 or タスク追加
3. googletasksにアップロード、ローカルjsonにもコピー

## 4. 入出力イメージ（完成形）
- **入力**：tasks -引数
- **出力**：タスク一覧 or タスクの追加完了
- **境界条件**：引数無い場合は一覧表示のみ

## 5. 機能要件
- 認証・ログイン処理
- データ保存
- データ取得
- データ加工
- データ送信
