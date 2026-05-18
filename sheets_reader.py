"""
Google Sheets 讀取與快取層
"""
import os
import json
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1K3VVKGJn47UTxGy7UGQtnkrO5yDVR9Bp7fHjMDVkv7w'

class SheetsCache:
    """簡單的記憶體快取，30分鐘刷新"""
    def __init__(self, cache_minutes=30):
        self.data = None
        self.last_updated = None
        self.cache_minutes = cache_minutes

    def is_valid(self):
        if self.data is None or self.last_updated is None:
            return False
        elapsed = datetime.now() - self.last_updated
        return elapsed < timedelta(minutes=self.cache_minutes)

    def get(self):
        if self.is_valid():
            return self.data
        return None

    def set(self, data):
        self.data = data
        self.last_updated = datetime.now()

_cache = SheetsCache()

def get_sheets_service():
    """取得 Google Sheets API 服務

    支援三種認證方式：
    1. Service Account (雲端優先)
    2. OAuth token.pickle (本地備用)
    3. OAuth 互動式登入
    """
    creds = None

    # 1. Service Account 認證 (優先 - 更穩定)
    if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
        try:
            service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
            return build('sheets', 'v4', credentials=creds)
        except Exception as e:
            print(f"Service Account 認證失敗: {e}")

    # 2. OAuth token.pickle 認證 (備用 - 本地開發)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

        if creds and creds.valid:
            return build('sheets', 'v4', credentials=creds)

        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                return build('sheets', 'v4', credentials=creds)
            except:
                pass

    # 3. OAuth 互動式登入
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)

def parse_date(date_str):
    """解析 M/D 格式的日期字符串

    Returns: (month, day) tuple or None
    """
    try:
        parts = date_str.strip().split('/')
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
    except:
        pass
    return None

def get_date_range(start_date=None, end_date=None):
    """取得日期範圍

    Args:
        start_date: (month, day) tuple，None 則預設為過去 14 天
        end_date: (month, day) tuple

    Returns: (datetime, datetime) tuple
    """
    if start_date and end_date:
        start_month, start_day = start_date
        end_month, end_day = end_date
        week_start = datetime(2026, start_month, start_day)
        week_end = datetime(2026, end_month, end_day)
    else:
        today = datetime.now()
        week_start = today - timedelta(days=14)
        week_end = today

    return week_start, week_end

def is_in_range(date_tuple, start_date=None, end_date=None):
    """檢查日期是否在範圍內"""
    if not date_tuple:
        return False

    month, day = date_tuple
    week_start, week_end = get_date_range(start_date, end_date)

    try:
        check_date = datetime(2026, month, day)
    except:
        return False

    return week_start <= check_date <= week_end

def fetch_raw_data(start_date=None, end_date=None, force_refresh=False):
    """從 Google Sheets 拉取原始數據

    Returns: list of rows (each row is [date, large_cat, designer, category, project])
    """
    # 檢查快取（僅當沒有日期過濾時）
    if not force_refresh and not start_date and not end_date:
        cached = _cache.get()
        if cached is not None:
            return cached

    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SHEET_ID, range='2026').execute()
    values = result.get('values', [])

    # 過濾並追溯「同上」
    filtered_rows = []
    last_project = None
    last_designer = None

    for i in range(3, len(values)):
        row = values[i] if i < len(values) else []

        if not row or len(row) == 0:
            continue

        date_str = row[0] if len(row) > 0 else ''

        # 跳過空行和只含中文的行（如「01月」）
        if not date_str or date_str.strip() in ['01月', '02月', '03月', '04月', '05月', '06月', '07月', '08月', '09月', '10月', '11月', '12月']:
            continue

        date_tuple = parse_date(date_str)
        if not is_in_range(date_tuple, start_date, end_date):
            continue

        # 提取欄位
        large_cat = row[1] if len(row) > 1 else ''
        designer = row[2] if len(row) > 2 else ''
        category = row[3] if len(row) > 3 else ''
        project = row[4] if len(row) > 4 else ''

        # 追溯「同上」
        if '同上' in project:
            actual_project = last_project if last_project else project
            actual_designer = last_designer if last_designer else designer
            is_carry_over = True
        else:
            actual_project = project
            actual_designer = designer
            is_carry_over = False
            last_project = project
            last_designer = designer

        filtered_rows.append({
            'date_str': date_str,
            'date_tuple': date_tuple,
            'large_cat': large_cat,
            'designer': actual_designer,
            'category': category,
            'project': actual_project,
            'is_carry_over': is_carry_over
        })

    # 僅當沒有日期過濾時快取結果
    if not start_date and not end_date:
        _cache.set(filtered_rows)

    return filtered_rows

def aggregate_by_designer(rows):
    """按設計師統計案件數

    Returns: {designer: count}
    """
    stats = defaultdict(int)
    for row in rows:
        if row['designer']:
            stats[row['designer']] += 1
    return dict(stats)

def aggregate_by_category(rows):
    """按類別統計案件數

    Returns: {category: count}
    """
    stats = defaultdict(int)
    for row in rows:
        if row['category']:
            stats[row['category']] += 1
    return dict(stats)

def aggregate_by_dimension(rows, classifier):
    """按維度統計案件數

    Args:
        rows: 原始數據行
        classifier: 分類器模組（含 classify_dimension 函數）

    Returns: {dimension: count}
    """
    stats = defaultdict(int)
    for row in rows:
        dimensions = classifier.classify_dimension(row['project'])
        for dim in dimensions:
            stats[dim] += 1
    return dict(stats)

def aggregate_by_unit(rows, classifier):
    """按案件單位統計

    Args:
        rows: 原始數據行
        classifier: 分類器模組（含 classify_project 函數）

    Returns: {unit: count}
    """
    stats = defaultdict(int)
    for row in rows:
        unit = classifier.classify_project(row['project'])
        if unit:  # 忽略 None（同上項目）
            stats[unit] += 1
    return dict(stats)

def aggregate_by_material_type(rows, classifier):
    """按素材類型統計

    Args:
        rows: 原始數據行
        classifier: 分類器模組（含 identify_material_type 函數）

    Returns: {material_type: count}
    """
    stats = defaultdict(int)
    for row in rows:
        material_type = classifier.identify_material_type(row['category'], row['project'])
        if material_type:
            stats[material_type] += 1
    return dict(stats)

def get_summary_stats(rows):
    """計算摘要統計

    Returns: {
        'total': int,
        'by_designer': {...},
        'unique_projects': int
    }
    """
    unique_projects = set()
    for row in rows:
        unique_projects.add(row['project'])

    return {
        'total': len(rows),
        'unique_projects': len(unique_projects),
        'by_designer': aggregate_by_designer(rows)
    }

def get_daily_stats(rows):
    """按日期統計每日案件數

    Returns: {date_str: count}
    """
    stats = defaultdict(int)
    for row in rows:
        stats[row['date_str']] += 1

    # 按日期排序
    sorted_stats = sorted(stats.items(), key=lambda x: parse_date(x[0]) or (99, 99))
    return dict(sorted_stats)

def clear_cache():
    """清除快取"""
    _cache.data = None
    _cache.last_updated = None
