import os.path
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DEFAULT_TASKLISTS = "MDA5MzEyNzMxNzEzMjczODUxNjg6MDow"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]

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

def items_show(service):
  result = service.tasks().list(tasklist=DEFAULT_TASKLISTS).execute()
  items = result.get("items", [])
  
  if not items:
    print("No task lists found.")
    return
  
  print("Task")
  for item in items:
    print("---")
    due = item.get("due", "None")
    title = item.get("title", "NoTitle")
    notes = item.get("notes", "None")
    print(f"期限: {due}\nタイトル: {title}\nメモ: {notes}")

def add_item(service,title,due=None,notes=None):
  body = {"title": title}
  if due:
    dt=due.split(",")
    body["title"] = f"({dt[1]}){title}"
    body["due"] = format_due(due)
  if notes:
    body["notes"] = notes
  service.tasks().insert(tasklist=DEFAULT_TASKLISTS,body=body).execute()

def main():
  creds=login()
  try:
    service = build("tasks", "v1", credentials=creds)
    due = "11/18,23:59"
    add_item(service,"test",due)
    
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()

