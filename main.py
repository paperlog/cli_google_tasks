import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]

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

def main():
  creds=login()
  try:
    service = build("tasks", "v1", credentials=creds)
    
    results = service.tasklists().list(maxResults=10).execute()
    items = results.get("items", [])
    
    if not items:
      print("No task lists found.")
      return
    
    print("Task lists:")
    for item in items:
      print(f"{item['title']} ({item['id']})")
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()

