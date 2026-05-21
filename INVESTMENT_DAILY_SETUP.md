# 投資日報自動發佈設置指南

## 📋 概覽
投資日報網頁已準備好在 GitHub Pages 上發佈，並支持每天早上 8 點自動更新。

## ✅ 已完成的設置

1. ✓ `investment-daily.html` - 投資日報網頁（含互動功能）
2. ✓ `update_investment_daily.py` - 自動更新腳本
3. ✓ `.github/workflows/update-daily-investment.yml` - 定時更新工作流程

## 🚀 接下來的設置步驟

### 第 1 步：重新生成 GitHub Token（含 workflow 權限）

1. 前往 https://github.com/settings/tokens
2. 點擊「Generate new token」→「Generate new token (classic)」
3. **Token 名稱**：`investment-daily-automation`
4. **有效期**：選 90 天或更長
5. **勾選以下權限**：
   - ✅ `repo` (完整控制)
   - ✅ `workflow` (管理 GitHub Actions 工作流程)
   - ✅ `read:public_key`
6. 複製 token（只會顯示一次！）

### 第 2 步：更新本地 Git 設置

```bash
# 在專案目錄中執行
git remote set-url origin https://[新token]@github.com/ananangela/designer-dashboard.git

# 測試連線
git fetch
```

### 第 3 步：推送工作流程文件

```bash
# 推送之前未成功的提交
git push

# 驗證推送成功
git log --oneline -3
```

### 第 4 步：在 GitHub 上設置 Secrets

1. 前往 https://github.com/ananangela/designer-dashboard/settings/secrets/actions
2. 點擊「New repository secret」
3. **名稱**：`ANTHROPIC_API_KEY`
4. **值**：你的 Claude API key（需要有足夠的額度）
5. 點擊「Add secret」

### 第 5 步：啟用 GitHub Pages

1. 前往 https://github.com/ananangela/designer-dashboard/settings
2. 左側選「Pages」
3. **Source** 選「Deploy from a branch」
4. **Branch** 選「main」，資料夾選「/ (root)」
5. 點「Save」

等待 1-2 分鐘，你的網頁會在以下位址發佈：
```
https://ananangela.github.io/designer-dashboard/investment-daily.html
```

### 第 6 步：測試自動更新工作流程

1. 前往 https://github.com/ananangela/designer-dashboard/actions
2. 選「📰 每日投資日報更新」工作流程
3. 點「Run workflow」→「Run workflow」（手動觸發）
4. 等待執行完成（通常 2-3 分鐘）

✅ 如果成功，你會看到：
- ✓ 工作流程狀態為「completed」
- ✓ investment-daily.html 中的 DATA 已更新
- ✓ GitHub Pages 上的網頁自動更新

## 📅 自動執行時間表

- **定時執行**：每天早上 8:00 (台灣時間 UTC+8)
  - 對應 GitHub Actions 時間：前一天 00:00 UTC
- **手動執行**：隨時可在 Actions 頁面手動觸發
- **首次執行**：設置完成後的下一個定時時間點

## 🔍 監控和故障排除

### 查看執行日誌

1. 前往 Actions 頁面
2. 選最新的「📰 每日投資日報更新」工作流程
3. 檢查各步驟的輸出

### 常見問題

**Q: 工作流程執行失敗？**
- 檢查 `ANTHROPIC_API_KEY` secret 是否正確設置
- 檢查 API 配額是否足夠
- 查看工作流程日誌了解詳細錯誤訊息

**Q: GitHub Pages 還沒有發佈？**
- 可能需要等待 1-2 分鐘
- 在 settings → Pages 檢查發佈狀態
- 清除瀏覽器快取重新載入

**Q: 文章內容沒有更新？**
- 確認工作流程執行成功（Actions 頁面檢查）
- 確認 investment-daily.html 在 GitHub 上已更新
- GitHub Pages 可能需要 1-2 分鐘重新部署

## 📱 網頁特性

投資日報網頁支持：
- ✅ 日期導航（前一天/後一天）
- ✅ 分類篩選（全部/股票/ETF/產業）
- ✅ 互動式術語卡片（點擊展開詳細說明）
- ✅ 日報測驗（測試前一天的知識）
- ✅ 完全響應式設計（手機/平板/桌面）

## 🛠️ 技術細節

### 更新流程
1. GitHub Actions 定時觸發工作流程
2. Python 腳本執行以下步驟：
   - 使用 Claude API 搜尋最新台灣財經新聞
   - 根據標準挑選最合適的文章
   - 自動整理成摘要、重點和術語解釋
   - 更新 investment-daily.html 中的 DATA 物件
   - 提交並推送到 GitHub
3. GitHub Pages 自動發佈最新版本

### 選文標準
- 有明確的單一主題（公司/ETF/產業）
- 包含具體的數字和事實
- 對初學者有教育價值
- 足夠有深度和可信度

## ❓ 需要幫助？

如果設置過程中遇到問題：
1. 檢查所有步驟是否完成
2. 查看 GitHub Actions 的工作流程日誌
3. 確認所有 secrets 和權限設置正確

祝你使用愉快！📊
