#!/usr/bin/env python3
"""
驗證設計團隊儀表板的設置
"""
import os
import sys

def check_file_exists(filepath, name):
    """檢查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - 未找到")
        return False

def check_directory_exists(dirpath, name):
    """檢查目錄是否存在"""
    if os.path.isdir(dirpath):
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - 未找到")
        return False

def check_python_package(package_name):
    """檢查 Python 包是否可導入"""
    try:
        __import__(package_name)
        print(f"✓ Python 包: {package_name}")
        return True
    except ImportError:
        print(f"✗ Python 包: {package_name} - 未安裝")
        return False

def main():
    print("=" * 60)
    print("設計團隊工作數據儀表板 - 設置驗證")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    all_good = True

    # 檢查文件
    print("\n【核心文件檢查】")
    all_good &= check_file_exists('app.py', 'app.py (Flask 主應用)')
    all_good &= check_file_exists('classifier.py', 'classifier.py (分類邏輯)')
    all_good &= check_file_exists('sheets_reader.py', 'sheets_reader.py (Sheets 讀取)')
    all_good &= check_file_exists('requirements.txt', 'requirements.txt (依賴)')

    # 檢查目錄
    print("\n【目錄結構檢查】")
    all_good &= check_directory_exists('templates', 'templates/ 目錄')
    all_good &= check_file_exists('templates/index.html', 'templates/index.html (前端)')

    # 檢查配置文件
    print("\n【配置文件檢查】")
    all_good &= check_file_exists('.env.example', '.env.example')
    all_good &= check_file_exists('render.yaml', 'render.yaml (Render 部署)')
    all_good &= check_file_exists('STARTUP.md', 'STARTUP.md (啟動指南)')

    # 檢查 Python 包
    print("\n【Python 包檢查】")
    required_packages = ['flask', 'google', 'dateutil']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ Python 包: {package}")
        except ImportError:
            print(f"✗ Python 包: {package} - 未安裝（執行: pip install -r requirements.txt）")
            all_good = False

    # 檢查認證文件
    print("\n【認證文件檢查】")
    if os.path.exists('credentials.json'):
        print("✓ credentials.json (OAuth 認證)")
    elif os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'):
        print("✓ GOOGLE_SERVICE_ACCOUNT_JSON 環境變數已設置")
    else:
        print("✗ 未找到認證文件或環境變數")
        print("  → 本地開發: 放置 credentials.json")
        print("  → 雲端部署: 設置 GOOGLE_SERVICE_ACCOUNT_JSON 環境變數")
        all_good = False

    # 最終結果
    print("\n" + "=" * 60)
    if all_good:
        print("✓ 設置完成！可以運行: python app.py")
    else:
        print("✗ 設置不完整。請按照 STARTUP.md 完成設置")
        print("=" * 60)
        sys.exit(1)
    print("=" * 60)

if __name__ == '__main__':
    main()
