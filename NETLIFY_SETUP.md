# 🚀 Netlify + 本地 Ollama 完全免費方案

## 📋 概覽

- ✅ **Netlify**：免費部署靜態網站
- ✅ **Ollama**：免費本地 AI（無需 Claude API）
- ✅ **cron-job.org**：免費定時服務
- ✅ **GitHub Pages/Netlify**：自動發佈
- 💰 **成本**：完全免費

---

## ⚙️ 前置準備

### 1️⃣ 安裝 Ollama（本地 AI）

**macOS：**
```bash
brew install ollama
```

或直接下載：https://ollama.ai

### 2️⃣ 下載模型

```bash
# 啟動 Ollama（保持運行）
ollama serve

# 在新終端下載模型
ollama pull mistral
# 或用中文更好的：
ollama pull neural-chat
```

等待 5-10 分鐘下載 (~4GB)

### 3️⃣ 測試 Ollama

```bash
curl http://localhost:11434/api/tags
# 應該返回已安裝的模型列表
```

---

## 🌐 Netlify 部署

### 第 1 步：連接到 Netlify

1. 前往 https://netlify.com
2. 用 GitHub 帳號登入
3. 點「New site from Git」
4. 選「GitHub」→ 授權
5. 選擇 `ananangela/designer-dashboard`
6. **Build command**：留空
7. **Publish directory**：`.`（根目錄）
8. 點「Deploy site」

✅ 網站已在 Netlify 上：`https://your-site.netlify.app`

### 第 2 步：設置自動更新 Hook

在 Netlify 中：

1. 進入 **Site settings** → **Build & deploy**
2. 左側選 **Build hooks**
3. 點「Add build hook」
   - **Name**：`daily-update`
   - **Branch**：`main`
4. 複製生成的 URL（如 `https://api.netlify.com/build_hooks/xxx`）

---

## ⏰ 設置定時更新

### 方案 A：使用 cron-job.org（推薦）

完全免費，無需本機運行。

1. 前往 https://cron-job.org/
2. 註冊免費帳號
3. 點「Create cron job」
4. 設置：
   - **URL**：貼上上面的 Netlify Build Hook URL
   - **Schedule**：每天 08:00（UTC+8 = UTC+0 時間）
   - **Timeout**：300 秒
5. 點「Create」

✅ 每天早上 8 點自動部署

### 方案 B：使用本機定時任務（需保持電腦開啟）

```bash
# macOS 用 launchd
# 編輯 ~/Library/LaunchAgents/com.investment-daily.plist
# 或 Linux 用 crontab
```

---

## 🤖 運行更新腳本（本地）

### 手動執行

```bash
cd /path/to/designer_dashboard

# 確保 Ollama 運行中
ollama serve  # 在另一個終端

# 運行更新腳本
python update_investment_daily_free.py
```

### 查看效果

1. 訪問：https://ananangela.github.io/designer-dashboard/investment-daily.html
2. 或 Netlify 上的網址
3. 檢查最新文章已更新 ✅

---

## 🔄 完整流程

```
1. 每天 08:00
   ↓
2. cron-job.org 觸發 Netlify Build Hook
   ↓
3. Netlify 從 GitHub 拉取最新代碼
   ↓
4. 你的本機（開啟時）運行更新腳本
   ↓
5. 腳本調用本地 Ollama 生成文章
   ↓
6. 更新 investment-daily.html
   ↓
7. git push 到 GitHub
   ↓
8. Netlify 自動部署
   ↓
9. 網站更新完成 ✅
```

---

## 📝 注意事項

### Ollama 需求

- **必須**：Ollama 在你的電腦上運行 (`ollama serve`)
- **建議**：電腦在每天早上 8 點左右開啟
- 或：使用雲服務（Railway/Render）來跑 Ollama 和更新腳本

### 替代方案（無需本機 Ollama）

如果你想完全不依賴本機：

1. **Railway/Render 免費層**：部署 Ollama + 更新腳本
2. **GitHub Actions**：每天自動運行（但需要 API Key）
3. **Replit**：免費雲端環境

---

## 🆘 故障排除

**問題：Ollama 連接失敗**
```
❌ Ollama 未運行
```
解決：
```bash
ollama serve  # 保持運行
```

**問題：Git push 失敗**

檢查 GitHub 認證：
```bash
git remote -v
gh auth status
```

**問題：Netlify 未自動部署**

檢查 Build Hook：
- Netlify 設置中的 Build hooks 是否正確
- cron-job.org 是否正確觸發（查看日誌）

---

## 💡 優化建議

1. **使用更輕量級的模型**
   ```bash
   ollama pull orca-mini  # 更小更快
   ollama pull phi        # 最小的
   ```

2. **設置更新通知**
   - 在腳本完成時發送 Slack/Email 通知

3. **備份舊文章**
   - 定期備份 `investment-daily.html`

---

## ✅ 檢查清單

- [ ] Ollama 已安裝 (`brew install ollama`)
- [ ] 模型已下載 (`ollama pull mistral`)
- [ ] Netlify 帳號已創建
- [ ] GitHub repo 已連接到 Netlify
- [ ] Build Hook 已生成並複製
- [ ] cron-job.org 已設置（或其他定時服務）
- [ ] 第一次手動更新成功
- [ ] 網站已更新 ✅

完成以上步驟，你就有一個**完全免費、自動更新的投資日報系統**了！🎉
