#!/usr/bin/env python3
"""
設計團隊工作數據儀表板 - Flask 後端
"""
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import classifier
import sheets_reader

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

def get_week_date_range(week_offset=0):
    """取得週的開始和結束日期

    Args:
        week_offset: 0 = 本週, -1 = 上週, etc.
    """
    today = datetime.now()
    # 找到週一（假設週一 = 工作週開始）
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)

    if week_offset != 0:
        monday = monday + timedelta(weeks=week_offset)

    sunday = monday + timedelta(days=6)

    return (
        (monday.month, monday.day),
        (sunday.month, sunday.day)
    )

def get_month_date_range(month_offset=0):
    """取得月的開始和結束日期

    Args:
        month_offset: 0 = 本月, -1 = 上月, etc.
    """
    today = datetime.now()
    current_year = today.year
    current_month = today.month

    # 計算目標月份
    target_month = current_month + month_offset

    # 處理年份邊界
    if target_month <= 0:
        current_year -= 1
        target_month += 12
    elif target_month > 12:
        current_year += 1
        target_month -= 12

    # 月初
    month_start = datetime(current_year, target_month, 1)

    # 月末 (下月初減 1 天)
    if target_month == 12:
        next_month_start = datetime(current_year + 1, 1, 1)
    else:
        next_month_start = datetime(current_year, target_month + 1, 1)
    month_end = next_month_start - timedelta(days=1)

    return (
        (month_start.month, month_start.day),
        (month_end.month, month_end.day)
    )

def get_filtered_rows(start_date=None, end_date=None):
    """取得過濾後的數據行"""
    if start_date and end_date:
        rows = sheets_reader.fetch_raw_data(start_date, end_date, force_refresh=False)
    else:
        rows = sheets_reader.fetch_raw_data(force_refresh=False)
    return rows

@app.route('/')
def dashboard():
    """儀表板主頁"""
    return render_template('index.html')

@app.route('/api/summary')
def api_summary():
    """取得案件摘要統計

    Returns:
    {
        'this_week': int,
        'last_week': int,
        'this_month': int,
        'last_month': int
    }
    """
    try:
        print("[DEBUG] Starting api_summary")
        # 本週
        this_week_start, this_week_end = get_week_date_range(0)
        this_week_rows = get_filtered_rows(this_week_start, this_week_end)
        this_week_count = len(this_week_rows)

        # 上週
        last_week_start, last_week_end = get_week_date_range(-1)
        last_week_rows = get_filtered_rows(last_week_start, last_week_end)
        last_week_count = len(last_week_rows)

        # 本月
        this_month_start, this_month_end = get_month_date_range(0)
        this_month_rows = get_filtered_rows(this_month_start, this_month_end)
        this_month_count = len(this_month_rows)

        # 上月
        last_month_start, last_month_end = get_month_date_range(-1)
        last_month_rows = get_filtered_rows(last_month_start, last_month_end)
        last_month_count = len(last_month_rows)

        return jsonify({
            'this_week': this_week_count,
            'last_week': last_week_count,
            'this_month': this_month_count,
            'last_month': last_month_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dimensions')
def api_dimensions():
    """取得維度分布

    Returns: [{name, count, percent}]
    """
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if start_date and end_date:
            start_date = tuple(map(int, start_date.split('/')))
            end_date = tuple(map(int, end_date.split('/')))
            rows = get_filtered_rows(start_date, end_date)
        else:
            rows = get_filtered_rows()

        dimension_stats = sheets_reader.aggregate_by_dimension(rows, classifier)

        total = sum(dimension_stats.values())
        result = [
            {
                'name': dim,
                'count': count,
                'percent': round((count / total * 100), 1) if total > 0 else 0
            }
            for dim, count in sorted(dimension_stats.items(), key=lambda x: x[1], reverse=True)
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/designers')
def api_designers():
    """取得設計師案件數對比

    Returns: [{name, this_week, last_week, this_month, last_month}]
    """
    try:
        # 本週
        this_week_start, this_week_end = get_week_date_range(0)
        this_week_rows = get_filtered_rows(this_week_start, this_week_end)
        this_week_stats = sheets_reader.aggregate_by_designer(this_week_rows)

        # 上週
        last_week_start, last_week_end = get_week_date_range(-1)
        last_week_rows = get_filtered_rows(last_week_start, last_week_end)
        last_week_stats = sheets_reader.aggregate_by_designer(last_week_rows)

        # 本月
        this_month_start, this_month_end = get_month_date_range(0)
        this_month_rows = get_filtered_rows(this_month_start, this_month_end)
        this_month_stats = sheets_reader.aggregate_by_designer(this_month_rows)

        # 上月
        last_month_start, last_month_end = get_month_date_range(-1)
        last_month_rows = get_filtered_rows(last_month_start, last_month_end)
        last_month_stats = sheets_reader.aggregate_by_designer(last_month_rows)

        # 合併結果 (以本週設計師為基準)
        all_designers = set()
        all_designers.update(this_week_stats.keys())
        all_designers.update(last_week_stats.keys())

        result = [
            {
                'name': designer,
                'this_week': this_week_stats.get(designer, 0),
                'last_week': last_week_stats.get(designer, 0),
                'this_month': this_month_stats.get(designer, 0),
                'last_month': last_month_stats.get(designer, 0)
            }
            for designer in sorted(all_designers)
            if designer
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def api_categories():
    """取得案件類別分布

    Returns: [{name, count, percent}]
    """
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if start_date and end_date:
            start_date = tuple(map(int, start_date.split('/')))
            end_date = tuple(map(int, end_date.split('/')))
            rows = get_filtered_rows(start_date, end_date)
        else:
            rows = get_filtered_rows()

        category_stats = sheets_reader.aggregate_by_category(rows)

        # 移除空值
        category_stats = {k: v for k, v in category_stats.items() if k}

        total = sum(category_stats.values())
        result = [
            {
                'name': cat,
                'count': count,
                'percent': round((count / total * 100), 1) if total > 0 else 0
            }
            for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/units')
def api_units():
    """取得案件單位分布

    Returns: [{name, count, percent}]
    """
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if start_date and end_date:
            start_date = tuple(map(int, start_date.split('/')))
            end_date = tuple(map(int, end_date.split('/')))
            rows = get_filtered_rows(start_date, end_date)
        else:
            rows = get_filtered_rows()

        unit_stats = sheets_reader.aggregate_by_unit(rows, classifier)

        # 移除空值
        unit_stats = {k: v for k, v in unit_stats.items() if k}

        total = sum(unit_stats.values())
        result = [
            {
                'name': unit,
                'count': count,
                'percent': round((count / total * 100), 1) if total > 0 else 0
            }
            for unit, count in sorted(unit_stats.items(), key=lambda x: x[1], reverse=True)
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/daily_trend')
def api_daily_trend():
    """取得每日工作量趨勢

    Returns: [{date, count}]
    """
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')

        if start_date and end_date:
            start_date = tuple(map(int, start_date.split('/')))
            end_date = tuple(map(int, end_date.split('/')))
            rows = get_filtered_rows(start_date, end_date)
        else:
            rows = get_filtered_rows()

        daily_stats = sheets_reader.get_daily_stats(rows)

        result = [
            {'date': date, 'count': count}
            for date, count in daily_stats.items()
        ]

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """強制重新從 Google Sheets 拉取數據"""
    try:
        sheets_reader.clear_cache()
        sheets_reader.fetch_raw_data(force_refresh=True)
        return jsonify({'status': 'refreshed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
