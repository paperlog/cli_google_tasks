import os.path
import sys
import json
from datetime import datetime, timezone, timedelta, date
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TASKS_FILE = os.path.join(BASE_DIR, "tasks.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")
LOCAL_FILE = os.path.join(BASE_DIR, "local.json")
SHORTCUT_FILE = os.path.join(BASE_DIR, "shortcut.json")

DEFAULT_TASKLISTS = "MDA5MzEyNzMxNzEzMjczODUxNjg6MDow"

SCOPES = ["https://www.googleapis.com/auth/tasks"]

def json_write(file_path,items):
  """jsonファイルへの書き込み"""
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

def json_read(file_path):
  """jsonファイルの読み取り"""
  with open(file_path, "r", encoding="utf-8") as f:
    items = json.load(f)
  return items

def format_due(due):
  """日時をgoogleのtasksの形式に整形"""
  dt = f"2026/{due}"
  try:
    result = datetime.strptime(dt, "%Y/%m/%d,%H:%M")
    result = result.replace(tzinfo=timezone(timedelta(hours=9)))
    return  result.isoformat()
  except ValueError:
    return None

def get_next_target_day(target_str):
  target = {"月":0, "火":1, "水":2, "木":3, "金":4, "土":5, "日":6}
  target = target[target_str]
  today = date.today()
  now_week = today.weekday()
  step = target - now_week
  if step <= 0:
    step = 7 + step
  target_week = today + timedelta(days=step)
  return target_week.isoformat().split("-")

def login():
  """googleへのログイン、認証と認証済みであることの保存"""
  creds = None
  # ユーザーの認証情報(token.json)の確認
  if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
  # token.jsonなければログイン
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          CREDENTIALS_FILE, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # tokne.jsonの作成
    with open(TOKEN_FILE, "w") as token:
      token.write(creds.to_json())
  return creds

def init_service():
  try:
    creds=login()
    service = build("tasks", "v1", credentials=creds)
    synchronization(service)
    return service
  except Exception as err:
    print("通信できませんでした")
    return None

def items_show(items):
  """Task(items)の一覧表示"""
  is_due={"None":[],"Any":[]}
  for item in items:
    due = item.get("due", "None")
    title = item.get("title", "NoTitle")
    notes = item.get("notes", "None")
    is_due.get(due,is_due["Any"]).append([due,title,notes])
  is_due["Any"].sort()
  print("Task\n")
  print("- 期限あり")
  for due, title, notes in is_due["Any"]:
    print(f"\t- [{due[:10]}] {title}")
    if notes!="None":
      print(f"\t\t- {notes}")
  print("- 期限なし")
  for due, title, notes in is_due["None"]:
    print(f"\t- {title}")
    if notes!="None":
      print(f"\t\t- {notes}")
  print("\n以上")

def get_items(service):
  """google tasksからタスクの一覧取得"""
  result = service.tasks().list(tasklist=DEFAULT_TASKLISTS).execute()
  items = result.get("items", [])
  
  if not items:
    print("No task lists found.")
    return []

  return items

def make_body(title, due = None, notes = None):
  """title,due,notesからタスクデータの本体を作成"""
  body = {"title": title}
  if due:
    dt=due.split(",")
    body["title"] = f"({dt[1]}){title}"
    body["due"] = format_due(due)
  if notes:
    body["notes"] = notes
  return body

def add_item(service,body):
  """google tasksにタスクを追加する"""
  service.tasks().insert(tasklist=DEFAULT_TASKLISTS,body=body).execute()

def synchronization(service):
  """起動時の同期処理"""
  bodys = json_read(LOCAL_FILE)
  if not(bodys):
    return
  for body in bodys:
    add_item(service,body)
  json_write(LOCAL_FILE,[])

def shortcut(key):
  """shortcut.jsonのショートカット参照し実行"""
  shortcuts = json_read(SHORTCUT_FILE)
  shortcut = shortcuts[key]
  title = shortcut["title"]
  
  due = shortcut["due"]
  d = due["day"]
  t = due["time"]
  day = get_next_target_day(d)
  due = f"{day[1]}/{day[2]},"+t
  
  notes = shortcut["notes"]
  body = make_body(title,due,notes)
  service = init_service()
  if service != None:
    add_item(service,body)
    # 変更したタスク一覧取得しローカル保存
    items = get_items(service)
    json_write(TASKS_FILE,items)
  else:
    bodys = json_read(LOCAL_FILE)
    bodys.append(body)
    json_write(LOCAL_FILE,bodys)
  print("追加完了")

def main():
  # コマンドライン引数取得
  args = sys.argv
  
  if len(args) == 1:
    # 引数なしのときタスク一覧表示
    # 通信：可
    service = init_service()
    if service != None:
      items = get_items(service)
      items_show(items)
      # ローカルへタスク一覧保存
      json_write(TASKS_FILE,items)
    else:
      # 通信：不可
      items = json_read(TASKS_FILE)
      items_show(items)
  else:
    if args[1][0] == "-":
      if args[1] == "-c":
        items = json_read(TASKS_FILE)
        items_show(items)
        return 0
      # 事前に決めたショートカットの実行(例：-test のときtitle="test",due="次の火曜",notes="")
      shortcut(args[1])
    else:
      # タスクの追加
      title = args[1]
      due = None
      notes = None
      if 3==len(args):
        due = format_due(args[2])
        if due == None:
          notes = args[2]
        else:
          due = args[2]
      if len(args)>=4:
        due = args[2]
        notes = args[3]
      body = make_body(title,due,notes)
      service = init_service()
      if service != None:
        add_item(service,body)
        # 変更したタスク一覧取得しローカル保存
        items = get_items(service)
        json_write(TASKS_FILE,items)
      else:
        bodys = json_read(LOCAL_FILE)
        bodys.append(body)
        json_write(LOCAL_FILE,bodys)
            
      print("追加完了")

if __name__ == "__main__":
  main()

