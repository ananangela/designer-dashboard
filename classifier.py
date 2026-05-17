"""
工作項目分類邏輯 - 從現有腳本移植
"""

def classify_dimension(project_name):
    """根據項目名稱識別營運維度

    Returns: list of dimensions or ['其他']
    """
    dimensions = []

    if not project_name:
        return dimensions

    project = project_name.lower()

    # 優先判斷：拉新留存維度（明確包含「拉新」）
    if '拉新' in project:
        dimensions.append('拉新留存')
        return dimensions

    # 銷售維度
    if any(word in project for word in ['銷售', '銷售導向', '倒數版', '預購', 'upsell', '商品包']):
        dimensions.append('銷售')

    if any(word in project for word in ['大眾', '5月銷售', '早鳥']):
        dimensions.append('銷售')

    if 'carrie' in project or '課程短影音' in project:
        if '銷售' not in dimensions:
            dimensions.append('銷售')
        return dimensions

    # 內容維度
    if any(word in project for word in ['課程', 'excel', '影音課', 'ai投資術', '線上課', '美股etf']):
        dimensions.append('內容')

    if any(word in project for word in ['產業報告', '產業研究', '重電']):
        dimensions.append('內容')

    # 外廣維度
    if any(word in project for word in ['外廣', '外框', '短影音', '聯播', 'appier']):
        if '【拉新】' not in project:
            dimensions.append('外廣')

    return dimensions if dimensions else ['其他']


def classify_project(project_name):
    """根據項目名稱識別產品類別

    Returns: str (category name) or None for '同上' items
    """
    if not project_name:
        return '未分類'

    project = project_name.strip()

    # 檢查「同上」項目 - 返回 None，由呼叫者處理
    if '同上' in project:
        return None

    # 檢查「大眾X月銷售」 -> 大眾產品組合
    if '大眾' in project and '銷售' in project:
        return '大眾產品組合'

    # 檢查「影音【拉新】」 -> 大眾產品組合
    if '影音【拉新】' in project or '【拉新】' in project:
        return '大眾產品組合'

    # 檢查「協助行銷」 -> 其他
    if '協助行銷' in project and '錄製' in project:
        return '其他'

    # 檢查「產業」相關 -> 產業研究報告
    if '４月產業外廣素材' in project or '產業外廣' in project:
        return '產業研究報告'

    # 優先檢查課程相關（優先於地域相關詞）
    if any(word in project for word in ['影音課程', '線上課程', 'Excel財報', 'AI實戰投資術', '【影音課程', '【大眾影音課']):
        return '課程'

    # 檢查課程（泛）
    if '課程' in project:
        return '課程'

    # 原有的分類規則
    if any(word in project for word in ['籌碼K線', '籌K', '【籌K】']):
        return '籌碼K線'

    if any(word in project for word in ['起漲K線', '起K', '【起漲K線']):
        return '起漲K線'

    if '主動式ETF' in project:
        return '主動式ETF'

    if 'ETF' in project or 'etf' in project:
        return 'ETF'

    if any(word in project for word in ['美股K線', '美股', '台美股']):
        return '美股K線'

    if any(word in project for word in ['產業研究報告', '產業報告', '【產業報告', '【大眾－產業報告']):
        return '產業研究報告'

    # 檢查「跨職能」- 如果包含 AI、研究等字眼
    if any(word in project for word in ['AI', '研究', '跨職能']):
        return '跨職能'

    # 其他雜項
    return '其他'


def identify_material_type(category, project_name):
    """根據category和project_name識別素材類型

    Returns: str (material type)
    """
    if not category:
        category = ""

    category_lower = category.lower()
    project_lower = project_name.lower() if project_name else ""

    # 識別短影音
    if '短影音' in category or '短影音' in project_name:
        return '短影音'

    # 識別行銷素材（組）
    if any(word in category for word in ['行銷圖', '行銷素材', '外廣', '商品頁', '素材']) or \
       any(word in project_name for word in ['素材', 'BN', '切角']):
        return '行銷素材（組）'

    # 識別圈層
    if any(word in category for word in ['圈層', '圓餅圖', '表格', '視覺更新']):
        return '圈層'

    # 其他
    return '其他'


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
