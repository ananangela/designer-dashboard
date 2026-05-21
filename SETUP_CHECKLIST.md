# 🚀 投資日報自動化設置檢查清單

## ✅ 已完成

- ✅ **投資日報網頁** - `investment-daily.html` 已上傳
- ✅ **自動更新腳本** - `update_investment_daily.py` 已準備
- ✅ **GitHub Pages** - 已啟用
  - 🌐 網址：https://ananangela.github.io/designer-dashboard/investment-daily.html
  - 等待 1-2 分鐘後訪問上面的 URL

## ⏳ 待完成（3 步）

### 1️⃣ 建立工作流程文件

在 GitHub 網頁上建立工作流程文件：

**點擊此連結打開建立頁面：**
👉 https://github.com/ananangela/designer-dashboard/new/main?filename=.github/workflows/update-daily-investment.yml

**在編輯框中貼上以下內容：**

```yaml
name: 📰 每日投資日報更新

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  update-daily:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: 📥 檢出代碼
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: 🐍 設置 Python 環境
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: 📦 安裝依賴
        run: |
          python -m pip install --upgrade pip
          pip install anthropic

      - name: 🔐 設置 git 身份
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"

      - name: 🤖 運行投資日報更新
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python update_investment_daily.py

      - name: 📊 更新狀態檢查
        if: always()
        run: echo "工作流程完成時間：$(date -u +'%Y-%m-%d %H:%M:%S UTC')"
```

**點擊「Commit new file」完成**

### 2️⃣ 添加 API Key Secret

1. 前往：https://github.com/ananangela/designer-dashboard/settings/secrets/actions
2. 點擊「New repository secret」
3. **Name**：`ANTHROPIC_API_KEY`
4. **Value**：你的 Anthropic API Key
   - 不知道怎麼獲得？👇 看下面的「獲取 API Key」

### 3️⃣ （可選）自動化更新時間

工作流程預設設置：
- ⏰ **執行時間**：每天早上 8:00（台灣時間）
- 🔄 **手動觸發**：隨時可在 Actions 頁面手動運行

---

## 🔑 獲取 Anthropic API Key

1. 前往 https://console.anthropic.com/
2. 登入你的 Anthropic 帳號（或註冊新帳號）
3. 左側選「API keys」
4. 點「Create Key」
5. 給 key 起個名字（如 `investment-daily`）
6. 複製 key（只會顯示一次）
7. 回到步驟 2️⃣ 貼上此 key

---

## 📊 發佈地址

完成上述設置後，你的投資日報將在以下位置發佈：

```
https://ananangela.github.io/designer-dashboard/investment-daily.html
```

✨ 所有互動功能都支持：
- 日期導航
- 分類篩選
- 互動式術語卡片
- 日報測驗

---

## 🔍 監控和故障排除

### 查看工作流程執行日誌

1. 前往 https://github.com/ananangela/designer-dashboard/actions
2. 選「📰 每日投資日報更新」
3. 查看最新執行記錄

### 常見問題

**Q: 工作流程執行失敗？**
- 檢查 `ANTHROPIC_API_KEY` 是否正確設置
- 查看日誌中的具體錯誤訊息

**Q: GitHub Pages 還沒更新？**
- 可能需要 1-2 分鐘
- 清除瀏覽器快取
- 檢查 Settings → Pages 的發佈狀態

**Q: 每天沒有自動更新？**
- 確認工作流程文件已建立
- 確認 API Key 已設置
- 工作流程在 UTC 時間 00:00 執行（台灣時間 08:00）

---

完成所有步驟後，你就有一個完全自動化的投資日報系統了！🎉
