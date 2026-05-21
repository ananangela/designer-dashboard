#!/usr/bin/env python3
"""簡單的 OAuth token 生成腳本"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

print("開始 Google 認證流程...")
print("瀏覽器會自動打開，請用你的全曜帳號登入並授權")

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=8080)

with open('token.pickle', 'wb') as token:
    pickle.dump(creds, token)

print("✓ token.pickle 已成功生成！")
