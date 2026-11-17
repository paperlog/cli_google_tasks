import os.path
import sys
import json
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_TASKLISTS = "MDA5MzEyNzMxNzEzMjczODUxNjg6MDow"

SCOPES = ["https://www.googleapis.com/auth/tasks"]

def json_write(items):
  with open("tasks.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

def json_read():
  with open("tasks.json", "r", encoding="utf-8") as f:
    items = json.load(f)
  return items

def format_due(due):
  dt = f"2026/{due}"
  result = datetime.strptime(dt, "%Y/%m/%d,%H:%M")
  result = result.replace(tzinfo=timezone(timedelta(hours=9)))
  return  result.isoformat()

def login():
  creds = None
  # ユーザーの認証情報(token.json)の確認
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # token.jsonなければログイン
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # tokne.jsonの作成
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds

def items_show(items):
  print("Task")
  for item in items:
    print("---")
    due = item.get("due", "None")
    title = item.get("title", "NoTitle")
    notes = item.get("notes", "None")
    print(f"期限: {due}\nタイトル: {title}\nメモ: {notes}")
  print("---\n以上")

def get_items(service):
  result = service.tasks().list(tasklist=DEFAULT_TASKLISTS).execute()
  items = result.get("items", [])
  
  if not items:
    print("No task lists found.")
    return []

  return items

def make_body(title, due = None, notes = None):
  body = {"title": title}
  if due:
    dt=due.split(",")
    body["title"] = f"({dt[1]}){title}"
    body["due"] = format_due(due)
  if notes:
    body["notes"] = notes
  return body

def add_item(service,body):
  service.tasks().insert(tasklist=DEFAULT_TASKLISTS,body=body).execute()
  print("追加完了")

def main():
  creds=login()
  try:
    service = build("tasks", "v1", credentials=creds)

    args = sys.argv

    if len(args) == 1:
      items = get_items(service)
      items_show(items)
    else:
      if args[1][0] == "-":
        print()
      else:
        title = args[1]
        due = None
        notes = None
        if len(args)>=3:
          due = args[2]
        if len(args)>=4:
          notes = args[3]
        body = make_body(title,due,notes)
        add_item(service,body)
        items = get_items(service)
        json_write(items)
    
  except HttpError as err:
    print("通信できませんでした。ローカル保存されたタスクを表示します。")    
    items = json_read()
    items_show(items)

if __name__ == "__main__":
  main()

