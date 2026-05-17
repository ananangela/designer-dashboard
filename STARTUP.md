# 設計團隊工作數據儀表板 - 啟動指南

## 本地開發環境設置

### 1. 準備 Python 環境

```bash
cd /Users/a01-0220-0066/designer_dashboard

# 創建虛擬環境
python3 -m venv venv

# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. Google Sheets API 認證

#### 選項 A: 本地開發（使用 OAuth）

1. 從現有工作目錄複製 `credentials.json`：
   ```bash
   cp /Users/a01-0220-0066/designer_work_stats/credentials.json .
   ```

2. 運行應用時會自動開啟瀏覽器進行 OAuth 認證，生成 `token.pickle`

#### 選項 B: 雲端部署（使用 Service Account）

1. 到 [Google Cloud Console](https://console.cloud.google.com/)

2. 創建新的 Service Account：
   - 導航到「Service Accounts」
   - 點擊「Create Service Account」
   - 給予「Editor」角色

3. 創建金鑰：
   - 點擊新建的 Service Account
   - 進入「Keys」標籤
   - 點擊「Add Key」→「Create new key」
   - 選擇 JSON 格式下載

4. 將 JSON 內容轉換為單行並設定環境變數：
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
   ```

### 3. 運行應用

```bash
# 確保虛擬環境已激活
source venv/bin/activate

# 運行 Flask 開發服務器
python app.py
```

應用將在 `http://localhost:5000` 運行

## 部署到 Render

### 1. 準備 GitHub 倉庫

```bash
cd designer_dashboard
git init
git add .
git commit -m "Initial commit: Designer dashboard"
git remote add origin https://github.com/YOUR_USERNAME/designer_dashboard.git
git push -u origin main
```

### 2. 在 Render 上部署

1. 到 [Render.com](https://render.com/)
2. 點擊「New」→「Web Service」
3. 連接 GitHub 倉庫
4. 配置如下：
   - **Name**: designer-dashboard
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

5. 添加環境變數：
   - **GOOGLE_SERVICE_ACCOUNT_JSON**: 粘貼 Service Account JSON
   - **SHEET_ID**: `1K3VVKGJn47UTxGy7UGQtnkrO5yDVR9Bp7fHjMDVkv7w`

6. 點擊「Create Web Service」部署

## 文件結構

```
designer_dashboard/
├── app.py                 # Flask 主應用
├── classifier.py          # 分類邏輯（從舊腳本移植）
├── sheets_reader.py       # Google Sheets 讀取 & 快取
├── requirements.txt       # Python 依賴
├── render.yaml           # Render 部署配置
├── .env.example          # 環境變數示例
├── venv/                 # Python 虛擬環境
└── templates/
    └── index.html        # 儀表板前端
```

## API 端點

### 獲取摘要統計
```
GET /api/summary
```
返回: `{ this_week, last_week, this_month, last_month }`

### 獲取維度分布
```
GET /api/dimensions?start=4/1&end=4/30
```
返回: `[{ name, count, percent }]`

### 獲取設計師案件數
```
GET /api/designers
```
返回: `[{ name, this_week, last_week, this_month, last_month }]`

### 獲取案件類別
```
GET /api/categories?start=4/1&end=4/30
```
返回: `[{ name, count, percent }]`

### 獲取案件單位
```
GET /api/units?start=4/1&end=4/30
```
返回: `[{ name, count, percent }]`

### 獲取每日趨勢
```
GET /api/daily_trend?start=4/1&end=4/30
```
返回: `[{ date, count }]`

### 強制刷新數據
```
POST /api/refresh
```
返回: `{ status: "refreshed" }`

## 快取機制

- 數據在記憶體中快取 30 分鐘
- 調用 `/api/refresh` 清除快取並重新加載數據
- 生產環境中每 5 分鐘自動刷新（前端設定）

## 後續任務（v2）

- [ ] 集成 Jira Cloud API
- [ ] 添加設計師篩選功能
- [ ] 實現自定義日期範圍選擇
- [ ] 添加案件詳細列表視圖
- [ ] 性能優化和加載指示器

## 常見問題

### Q: 本地開發時出現「credentials.json 未找到」？
A: 確保 `credentials.json` 在 designer_dashboard 目錄中，或使用 Service Account 認證

### Q: 部署後看不到數據？
A: 檢查環境變數中的 `GOOGLE_SERVICE_ACCOUNT_JSON` 是否正確設定

### Q: 圖表加載很慢？
A: 這可能是因為 Google Sheets API 響應較慢。可以考慮：
1. 減少數據範圍
2. 使用 Service Account（比 OAuth 稍快）
3. 增加快取時間

## 聯絡支持

如有問題，請檢查 Flask 應用的日誌或瀏覽器控制台的錯誤信息。
