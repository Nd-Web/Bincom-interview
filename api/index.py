from flask import Flask, jsonify, request
import random
from math import sqrt
import os

app = Flask(__name__)

try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

import sqlite3


def get_color_data():
    """Scrape color data from webpage."""
    import requests
    from bs4 import BeautifulSoup

    url = "https://bincom.dev/test/"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table')
        if not table:
            return None
        colors = []
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                text = cell.get_text(strip=True)
                if text and text.lower() not in ['color', 'day', 'colors']:
                    colors.append(text)
        return colors if colors else None
    except:
        return None


def sample_colors():
    """Fallback sample data."""
    return [
        'RED', 'GREEN', 'YELLOW', 'BLUE', 'WHITE',
        'RED', 'GREEN', 'YELLOW', 'BLUE',
        'RED', 'GREEN', 'YELLOW',
        'RED', 'GREEN',
        'RED',
        'GREEN', 'YELLOW', 'BLUE', 'WHITE', 'BLACK',
        'YELLOW', 'BLUE', 'WHITE', 'BLACK',
        'BLUE', 'WHITE', 'BLACK',
        'WHITE', 'BLACK',
        'BLACK'
    ]


def mean_color(colors):
    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}
    nums = [color_idx[c] for c in colors]
    avg = sum(nums) / len(nums)
    nearest = min(round(avg), len(sorted_colors) - 1)
    return sorted_colors[nearest], {
        'mean_value': round(avg, 2),
        'color_mapping': color_idx
    }


def mode_color(colors):
    freq = {}
    for c in colors:
        freq[c] = freq.get(c, 0) + 1
    max_count = max(freq.values())
    modes = [c for c, f in freq.items() if f == max_count]
    return modes, {'frequencies': freq, 'max_count': max_count}


def median_color(colors):
    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}
    nums = sorted([color_idx[c] for c in colors])
    n = len(nums)
    if n % 2 == 1:
        mid_idx = nums[n // 2]
    else:
        mid_idx = round((nums[n//2 - 1] + nums[n//2]) / 2)
    return sorted_colors[mid_idx], {'sorted_values': nums}


def variance(colors):
    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}
    nums = [color_idx[c] for c in colors]
    n = len(nums)
    mean = sum(nums) / n
    var = sum((x - mean) ** 2 for x in nums) / n
    return var, {'mean': mean, 'std_dev': sqrt(var)}


def prob_red(colors):
    total = len(colors)
    reds = sum(1 for c in colors if c.upper() == 'RED')
    return reds / total, {'total': total, 'red_count': reds}


def save_to_db(colors):
    freq = {}
    for c in colors:
        freq[c] = freq.get(c, 0) + 1

    db_file = os.path.join(os.path.dirname(__file__), '..', 'colors.db')
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS color_frequency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            frequency INTEGER
        )
    ''')
    cur.execute("DELETE FROM color_frequency")
    for color, count in freq.items():
        cur.execute("INSERT INTO color_frequency (color, frequency) VALUES (?, ?)", (color, count))
    conn.commit()
    cur.execute("SELECT * FROM color_frequency ORDER BY frequency DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def binary_search(arr, target, left=0, right=None):
    if right is None:
        right = len(arr) - 1
    if left > right:
        return False, -1
    mid = (left + right) // 2
    if arr[mid] == target:
        return True, mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, right)
    else:
        return binary_search(arr, target, left, mid - 1)


@app.route('/')
def index():
    return jsonify({
        'message': 'Bincom Developer Test API',
        'endpoints': [
            '/api/colors',
            '/api/mean',
            '/api/mode',
            '/api/median',
            '/api/variance',
            '/api/probability/red',
            '/api/database',
            '/api/binary-search/<number>',
            '/api/binary-convert',
            '/api/fibonacci'
        ]
    })


@app.route('/api/colors')
def api_colors():
    colors = get_color_data() or sample_colors()
    return jsonify({'colors': colors, 'count': len(colors)})


@app.route('/api/mean')
def api_mean():
    colors = get_color_data() or sample_colors()
    result, details = mean_color(colors)
    return jsonify({'mean_color': result, 'details': details})


@app.route('/api/mode')
def api_mode():
    colors = get_color_data() or sample_colors()
    result, details = mode_color(colors)
    return jsonify({'mode_colors': result, 'details': details})


@app.route('/api/median')
def api_median():
    colors = get_color_data() or sample_colors()
    result, details = median_color(colors)
    return jsonify({'median_color': result, 'details': details})


@app.route('/api/variance')
def api_variance():
    colors = get_color_data() or sample_colors()
    result, details = variance(colors)
    return jsonify({'variance': result, 'std_dev': round(details['std_dev'], 4), 'mean': details['mean']})


@app.route('/api/probability/red')
def api_prob_red():
    colors = get_color_data() or sample_colors()
    result, details = prob_red(colors)
    return jsonify({'probability': result, 'details': details})


@app.route('/api/database')
def api_database():
    colors = get_color_data() or sample_colors()
    rows = save_to_db(colors)
    return jsonify({'saved': [{'id': r[0], 'color': r[1], 'frequency': r[2]} for r in rows]})


@app.route('/api/binary-search/<int:number>')
def api_binary_search(number):
    nums = list(range(1, 100, 2))  # odd numbers 1-99
    found, idx = binary_search(nums, number)
    return jsonify({
        'search_number': number,
        'found': found,
        'index': idx if found else None,
        'list': 'odd numbers 1-99'
    })


@app.route('/api/binary-convert')
def api_binary_convert():
    binary = ''.join(str(random.randint(0, 1)) for _ in range(4))
    decimal = int(binary, 2)
    return jsonify({'binary': binary, 'decimal': decimal})


@app.route('/api/fibonacci')
def api_fibonacci():
    n = request.args.get('n', 50, type=int)
    a, b = 0, 1
    total = 0
    fibs = []
    for _ in range(n):
        fibs.append(a)
        total += a
        a, b = b, a + b
    return jsonify({
        'n': n,
        'sum': total,
        'first_10': fibs[:10]
    })


# For Vercel
handler = app