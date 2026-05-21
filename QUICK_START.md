# 🚀 快速開始（5 分鐘）

## 完全免費方案：Netlify + 本地 Ollama

---

## 📝 現在就做（按順序）

### ① 安裝 Ollama（5 分鐘）

```bash
# macOS
brew install ollama

# 下載模型（會下載 ~4GB，等待 5-10 分鐘）
ollama pull mistral

# 啟動 Ollama（保持這個終端開啟）
ollama serve
```

✅ 看到 `Listening on 127.0.0.1:11434` 就成功了

---

### ② 部署到 Netlify（3 分鐘）

1. 前往 https://netlify.com （用 GitHub 登入）
2. 點「New site from Git」
3. 選 `ananangela/designer-dashboard`
4. 點「Deploy site」

✅ 等 1-2 分鐘，你的網站在：`https://your-site.netlify.app`

---

### ③ 設置自動更新（2 分鐘）

**在 Netlify 中：**
1. Settings → Build & deploy → Build hooks
2. 「Add build hook」→ 名稱 `daily-update`
3. 複製生成的 URL

**在 cron-job.org：**
1. 前往 https://cron-job.org （註冊）
2. Create cron job
3. **URL**：貼上上面的 URL
4. **Schedule**：`0 8 * * *`（每天 8 點）
5. Create

✅ 完成！

---

## 🧪 測試它

### 手動運行一次

```bash
cd /path/to/designer_dashboard

# 確保 Ollama 在運行（見上面）

# 運行更新腳本
python update_investment_daily_free.py
```

預期輸出：
```
🚀 投資日報更新開始
⏰ 2026-05-21 10:30:45
✓ Ollama 服務運行中
📰 生成投資日報內容...
✓ 文章標題：...
✓ HTML 已更新：2026-05-21
✓ 已推送到 GitHub
✅ 投資日報更新完成！
```

### 查看網站

訪問：https://your-site.netlify.app/investment-daily.html

✅ 看到最新文章了！

---

## 📊 自動運行時間表

| 時間 | 動作 |
|------|------|
| 每天 08:00 | cron-job.org 觸發 |
| → | Netlify 部署最新 git 版本 |
| → | 你的電腦執行 `update_investment_daily_free.py`（需開啟） |
| → | Ollama 生成新文章 |
| → | Push 到 GitHub |
| → | Netlify 自動重新部署 |
| → | ✅ 網站更新完成 |

---

## 💡 核心邏輯

```
Ollama（免費 AI）
    ↓
生成投資日報內容
    ↓
更新 investment-daily.html
    ↓
git push 到 GitHub
    ↓
Netlify 自動部署
    ↓
訪問網站看最新文章 ✅
```

---

## ⚠️ 重要提醒

### Ollama 必須運行

```bash
ollama serve  # 在另一個終端保持開啟
```

否則更新腳本會失敗。

### 如果不想本機開著

可以選擇：
1. **Railway/Render**：部署 Ollama + 腳本到雲端（免費層）
2. **GitHub Actions**：用 workflow 自動運行（見 `.github/workflows/update-daily-investment.yml`）

---

## 🆘 常見問題

**Q: 每天怎樣自動運行？**
A: 通過 cron-job.org 定時觸發 Netlify，你的電腦在那時需要開啟並運行 Ollama。

**Q: 可以完全不依賴本機嗎？**
A: 可以，用 Railway 或 Render 部署整個系統到雲端。

**Q: 生成的文章品質如何？**
A: Ollama 用開源模型（Mistral），品質接近 GPT-3.5，完全免費。

**Q: 成本多少？**
A: 0 元。Ollama、Netlify、cron-job 都是免費的。

---

## ✅ 檢查清單

- [ ] Ollama 已安裝並運行
- [ ] 模型已下載（mistral）
- [ ] 網站已部署到 Netlify
- [ ] Build Hook 已創建
- [ ] cron-job 已設置
- [ ] 手動執行成功
- [ ] 看到網站更新

完成所有項目後，你就有一個**完全自動、零成本的投資日報系統** 🎉

---

## 📚 詳細文檔

- `NETLIFY_SETUP.md` - 詳細設置步驟
- `update_investment_daily_free.py` - 更新腳本
- `investment-daily.html` - 網頁

有問題隨時問！
