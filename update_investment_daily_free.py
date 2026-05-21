#!/usr/bin/env python3
"""
投資日報每日更新腳本 - 使用本地 Ollama AI（完全免費）
每天早上 8 點自動搜尋台灣財經新聞，挑選並整理成投資日報
"""
import json
import re
import subprocess
from datetime import datetime, timedelta
import requests

# Ollama 本地 API
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # 或 "neural-chat"


def check_ollama():
    """檢查 Ollama 是否運行"""
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2)
        print("✓ Ollama 服務運行中")
        return True
    except:
        print("❌ Ollama 未運行。請執行：ollama serve")
        return False


def ollama_generate(prompt, system=""):
    """調用本地 Ollama 生成文本"""
    try:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = requests.post(
            OLLAMA_API,
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return result.get("response", "")
    except Exception as e:
        print(f"⚠️ Ollama 錯誤: {e}")
        return None


def search_news():
    """使用 Ollama 模擬搜尋和挑選新聞"""
    print("\n📰 生成投資日報內容...")

    # 系統提示詞
    system_prompt = """你是一個專業的財經新聞編輯，熟悉台灣股市和投資知識。
請根據今天的日期和一般台股市況，生成一篇適合投資初學者的日報文章。

文章應該包含：
1. 明確的單一主題（公司/ETF/產業）
2. 具體的數字和事實
3. 對初學者有教育價值的術語解釋
4. 3-5 個重點

生成一篇虛構但邏輯合理的投資日報。"""

    prompt = f"""
    請為 {datetime.now().strftime('%Y年%m月%d日')} 生成一篇投資日報。

    內容應該涵蓋台灣股市的某個熱門話題。

    以下是返回格式（JSON）：
    {{
        "headline": "標題（20-40字）",
        "deck": "摘要（30-50字）",
        "source": "新聞來源",
        "readingTime": 3,
        "difficulty": "beginner",
        "difficultyLabel": "初級",
        "tags": [{{"t":"stock", "l":"標籤"}}],
        "summary": "完整摘要（150-200字，用<strong>標記重點）",
        "keypoints": ["重點1", "重點2", "重點3"],
        "terms": [
            {{
                "name": "詞彙",
                "en": "English",
                "short": "簡短解釋",
                "full": "完整解釋",
                "eg": "實例"
            }}
        ]
    }}
    """

    content = ollama_generate(prompt, system_prompt)

    if not content:
        return None

    # 提取 JSON
    json_match = re.search(r'\{[\s\S]*\}', content)
    if json_match:
        try:
            article_data = json.loads(json_match.group())
            return article_data
        except json.JSONDecodeError:
            print("⚠️ JSON 解析失敗，嘗試修復...")
            return None

    return None


def update_html_file(article_data):
    """更新 investment-daily.html 中的 DATA 物件"""
    if not article_data:
        print("❌ 文章數據為空")
        return False

    try:
        with open("investment-daily.html", "r", encoding="utf-8") as f:
            content = f.read()

        today = datetime.now().strftime("%Y-%m-%d")
        dates = [today] + [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 5)]

        # 生成新的 DATA 條目
        article_json = json.dumps(article_data, ensure_ascii=False, indent=4)
        new_entry = f'  "{today}": {article_json},'

        # 更新 DATA 物件
        data_start = content.find('const DATA = {')
        if data_start != -1:
            insertion_point = content.find('{', data_start) + 1
            new_content = content[:insertion_point] + '\n' + new_entry + content[insertion_point:]
        else:
            print("❌ 找不到 DATA 物件")
            return False

        # 更新 DAYS 列表
        days_str = ', '.join(f'"{d}"' for d in dates)
        new_days_line = f'const DAYS = [{days_str}];'

        dates_start = new_content.find('const DAYS = ')
        if dates_start != -1:
            dates_end = new_content.find(';', dates_start)
            new_content = new_content[:dates_start] + new_days_line + new_content[dates_end+1:]

        # 更新 TODAY
        today_start = new_content.find('const TODAY = ')
        if today_start != -1:
            today_end = new_content.find(';', today_start)
            new_today_line = f'const TODAY = "{today}";'
            new_content = new_content[:today_start] + new_today_line + new_content[today_end+1:]

        with open("investment-daily.html", "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✓ HTML 已更新：{today}")
        return True

    except Exception as e:
        print(f"❌ 更新失敗：{e}")
        return False


def commit_and_push():
    """提交並推送到 GitHub"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        subprocess.run(["git", "add", "investment-daily.html"], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update investment daily: {today}"],
            check=True,
            capture_output=True
        )
        subprocess.run(["git", "push"], check=True, capture_output=True)

        print("✓ 已推送到 GitHub")
        return True

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git 操作出錯：{e}")
        return False


def main():
    """主流程"""
    print("🚀 投資日報更新開始")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 檢查 Ollama
    if not check_ollama():
        print("\n⚠️ 需要 Ollama 運行中...")
        print("請在另一個終端執行：ollama serve")
        return False

    # 生成文章內容
    article_data = search_news()
    if not article_data:
        print("❌ 無法生成文章")
        return False

    print(f"\n✓ 文章標題：{article_data.get('headline', 'N/A')}")

    # 更新 HTML
    if not update_html_file(article_data):
        return False

    # 推送到 GitHub
    if not commit_and_push():
        return False

    print("\n✅ 投資日報更新完成！")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
