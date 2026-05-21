#!/usr/bin/env python3
"""
投資日報每日更新腳本
每天早上 8 點自動搜尋台灣財經新聞，挑選並整理成投資日報
"""
import json
import re
from datetime import datetime, timedelta
from anthropic import Anthropic

client = Anthropic()


def get_date_range(days=5):
    """取得最近 N 天的日期列表 (YYYY-MM-DD)"""
    dates = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates


def search_news():
    """搜尋當天台灣財經新聞"""
    conversation = []

    # 第一輪：搜尋新聞
    search_prompt = """請幫我搜尋「台股 投資新聞 今日」相關的最新台灣財經新聞。

    搜尋後請列出前 5 篇新聞，格式為：
    1. [標題] - [來源]
    2. [標題] - [來源]
    ...

    並簡要說明每篇新聞的核心內容。"""

    conversation.append({"role": "user", "content": search_prompt})

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system="""你是一個專業的財經新聞編輯，熟悉台灣股市和投資知識。
你需要幫助用戶：
1. 搜尋最新的台灣財經新聞
2. 挑選適合投資初學者的文章
3. 整理成清晰的摘要和重點

選文標準：
- 有明確主題（一家公司 / 一個 ETF / 一個產業）
- 有可以解釋給初學者的名詞
- 有具體事件或數字
- 新聞的深度和品質足夠""",
        messages=conversation
    )

    news_summary = response.content[0].text
    conversation.append({"role": "assistant", "content": news_summary})

    # 第二輪：挑選最佳文章
    select_prompt = """從上面的新聞中，請挑選最符合以下標準的一篇：
    1. 有明確的單一主題（公司/ETF/產業）
    2. 包含具體的數字和事實
    3. 對初學者有教育價值
    4. 足夠有深度

    請說明你選擇這篇的理由，並提供：
    - 標題
    - 來源
    - 核心摘要（用初學者能理解的語言）"""

    conversation.append({"role": "user", "content": select_prompt})

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        system="""你是一個專業的財經新聞編輯，熟悉台灣股市和投資知識。
你需要幫助用戶：
1. 搜尋最新的台灣財經新聞
2. 挑選適合投資初學者的文章
3. 整理成清晰的摘要和重點

選文標準：
- 有明確主題（一家公司 / 一個 ETF / 一個產業）
- 有可以解釋給初學者的名詞
- 有具體事件或數字
- 新聞的深度和品質足夠""",
        messages=conversation
    )

    selection = response.content[0].text
    conversation.append({"role": "assistant", "content": selection})

    return selection, conversation


def generate_article_content(selection, conversation):
    """根據選定的新聞生成完整的文章內容"""

    gen_prompt = """現在請根據選定的新聞，生成一篇完整的投資日報文章。

    請提供以下內容（JSON 格式）：
    {
        "headline": "文章標題（20-40字）",
        "deck": "文章摘要（用初學者語言，30-50字）",
        "source": "新聞來源",
        "readingTime": 3-5,
        "difficulty": "beginner或intermediate",
        "difficultyLabel": "初級或進階",
        "tags": [{"t":"stock|etf|industry", "l":"標籤文字"}],
        "summary": "完整的文章摘要（150-200字，用<strong>標記重點詞彙）",
        "keypoints": ["重點1", "重點2", "重點3", "重點4", "重點5"],
        "terms": [
            {
                "name": "詞彙名稱",
                "en": "英文名稱",
                "short": "簡短解釋（30字內）",
                "full": "完整解釋（100字內）",
                "eg": "實例說明"
            }
        ]
    }

    注意：
    - 返回格式必須是有效的 JSON
    - terms 列表中至少要有 3 個詞彙
    - 所有內容要用繁體中文
    - summary 中的重點詞彙要用 <strong></strong> 標記"""

    conversation.append({"role": "user", "content": gen_prompt})

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=3000,
        system="""你是一個專業的財經新聞編輯和教育工作者。
你需要根據新聞內容生成適合初學者的投資日報文章。

文章的特點：
- 用初學者能理解的語言解釋概念
- 包含重要的經濟指標和術語
- 提供實用的投資知識
- 引用具體的數字和事實""",
        messages=conversation
    )

    article_json = response.content[0].text

    # 提取 JSON
    json_match = re.search(r'\{[\s\S]*\}', article_json)
    if json_match:
        try:
            article_data = json.loads(json_match.group())
            return article_data
        except json.JSONDecodeError:
            print("Warning: 無法解析 JSON，嘗試修復...")
            return None

    return None


def update_html_file(article_data):
    """更新 investment-daily.html 中的 DATA 對象"""

    if not article_data:
        print("Error: 文章數據為空")
        return False

    try:
        with open("investment-daily.html", "r", encoding="utf-8") as f:
            content = f.read()

        # 找到 DATA 對象的開始位置
        data_start = content.find('const DATA = {')
        if data_start == -1:
            print("Error: 找不到 DATA 對象")
            return False

        # 找到日期列表的開始位置
        dates_start = content.find('const DAYS = ', 0, data_start)
        if dates_start == -1:
            print("Error: 找不到 DAYS 列表")
            return False

        # 獲取當天日期
        today = datetime.now().strftime("%Y-%m-%d")

        # 生成新的 DATA 對象條目
        # 注意：需要轉義引號和特殊字符
        article_json = json.dumps(article_data, ensure_ascii=False)
        # 轉義以用在 JavaScript 中
        article_json_escaped = article_json.replace('"', '\\"').replace('\n', '')

        # 簡化方案：直接生成 JavaScript 語句
        new_entry = f'  "{today}": {json.dumps(article_data, ensure_ascii=False, indent=4)},'

        # 在 DATA 對象開始後插入新條目
        insertion_point = content.find('{', data_start) + 1
        new_content = content[:insertion_point] + '\n' + new_entry + content[insertion_point:]

        # 更新 DAYS 列表（如果需要）
        dates = get_date_range(5)
        days_str = ', '.join(f'"{d}"' for d in dates)
        new_days_line = f'const DAYS = [{days_str}];'

        # 替換 DAYS 列表
        days_end = content.find(';', dates_start)
        new_content = new_content[:dates_start] + new_days_line + new_content[days_end+1:]

        # 更新 TODAY
        today_start = content.find('const TODAY = ')
        if today_start != -1:
            today_end = content.find(';', today_start)
            new_today_line = f'const TODAY = "{today}";'
            new_content = new_content[:today_start] + new_today_line + new_content[today_end+1:]

        with open("investment-daily.html", "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✓ 成功更新 HTML 文件，日期：{today}")
        return True

    except Exception as e:
        print(f"Error: 更新 HTML 文件失敗 - {e}")
        return False


def commit_and_push():
    """提交更改到 GitHub"""
    import subprocess

    try:
        today = datetime.now().strftime("%Y-%m-%d")

        subprocess.run(["git", "add", "investment-daily.html"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update investment daily: {today}"],
            check=True
        )
        subprocess.run(["git", "push"], check=True)

        print("✓ 成功推送到 GitHub")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error: Git 操作失敗 - {e}")
        return False


def main():
    """主流程"""
    print("🚀 開始生成投資日報...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 搜尋新聞並挑選
        print("\n📰 搜尋台灣財經新聞...")
        selection, conversation = search_news()
        print(f"\n選文結果：\n{selection}")

        # 生成文章內容
        print("\n✍️  生成文章內容...")
        article_data = generate_article_content(selection, conversation)

        if not article_data:
            print("❌ 無法生成文章數據")
            return False

        print(f"\n文章標題：{article_data.get('headline', 'N/A')}")

        # 更新 HTML
        print("\n📝 更新 HTML 文件...")
        if not update_html_file(article_data):
            return False

        # 推送到 GitHub
        print("\n🔄 推送到 GitHub...")
        if not commit_and_push():
            return False

        print("\n✅ 投資日報更新完成！")
        return True

    except Exception as e:
        print(f"\n❌ 發生錯誤：{e}")
        return False


if __name__ == "__main__":
    main()
