#!/usr/bin/env python3
"""
Bincom Developer Test Solution
"""

import requests
from bs4 import BeautifulSoup
import os
import sys
import random
from math import sqrt

# Database imports
try:
    import psycopg2
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

import sqlite3


def get_color_data():
    """Scrape color data from the test webpage. Returns list of colors."""
    url = "https://bincom.dev/test/"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Find the table and extract colors
        table = soup.find('table')
        if not table:
            raise ValueError("No table found")

        colors = []
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                text = cell.get_text(strip=True)
                # Skip header text
                if text and text.lower() not in ['color', 'day', 'colors']:
                    colors.append(text)

        return colors if colors else None

    except Exception as e:
        print(f"Couldn't fetch webpage: {e}")
        return None


def sample_colors():
    """Fallback sample data when webpage unavailable."""
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


# Q1: Mean Color
def mean_color(colors):
    """Calculate mean color by mapping to numeric indices."""
    print("\nQ1: MEAN COLOR")
    print("-" * 40)

    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}

    nums = [color_idx[c] for c in colors]
    avg = sum(nums) / len(nums)

    # Round to nearest index
    nearest = round(avg)
    if nearest >= len(sorted_colors):
        nearest = len(sorted_colors) - 1

    result = sorted_colors[nearest]
    print(f"Colors mapped to indices: {color_idx}")
    print(f"Mean value: {avg:.2f} -> nearest color index: {nearest}")
    print(f">>> Mean Color: {result}")
    return result


# Q2: Mode Color
def mode_color(colors):
    """Find most frequently worn color."""
    print("\nQ2: MODE COLOR")
    print("-" * 40)

    freq = {}
    for c in colors:
        freq[c] = freq.get(c, 0) + 1

    max_count = max(freq.values())
    modes = [c for c, f in freq.items() if f == max_count]

    print(f"Frequencies: {freq}")
    if len(modes) == 1:
        print(f">>> Mode Color: {modes[0]} (appears {max_count} times)")
    else:
        print(f">>> Mode Colors (tie): {', '.join(modes)} (each appears {max_count} times)")

    return modes


# Q3: Median Color
def median_color(colors):
    """Find median color from numeric mapping."""
    print("\nQ3: MEDIAN COLOR")
    print("-" * 40)

    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}

    nums = sorted([color_idx[c] for c in colors])
    n = len(nums)

    if n % 2 == 1:
        mid_idx = nums[n // 2]
    else:
        mid_idx = round((nums[n//2 - 1] + nums[n//2]) / 2)

    result = sorted_colors[mid_idx]
    print(f"Sorted values: {nums}")
    print(f"Median position: {n//2}, value: {mid_idx}")
    print(f">>> Median Color: {result}")
    return result


# Q4: Variance
def variance(colors):
    """Calculate population variance."""
    print("\nQ4: VARIANCE")
    print("-" * 40)

    sorted_colors = sorted(set(colors))
    color_idx = {c: i for i, c in enumerate(sorted_colors)}

    nums = [color_idx[c] for c in colors]
    n = len(nums)
    mean = sum(nums) / n

    var = sum((x - mean) ** 2 for x in nums) / n

    print(f"Values: {nums}")
    print(f"Mean: {mean}")
    print(f">>> Variance: {var}")
    print(f">>> Std Dev: {sqrt(var):.4f}")
    return var


# Q5: Probability of Red
def prob_red(colors):
    """Calculate probability of selecting red."""
    print("\nQ5: PROBABILITY OF RED")
    print("-" * 40)

    total = len(colors)
    reds = sum(1 for c in colors if c.upper() == 'RED')
    prob = reds / total

    print(f"Total: {total}, Reds: {reds}")
    print(f">>> P(Red) = {prob}")
    return prob


# Q6: Database
def save_to_db(colors):
    """Save color frequencies to database (PostgreSQL or SQLite)."""
    print("\nQ6: DATABASE")
    print("-" * 40)

    # Count frequencies
    freq = {}
    for c in colors:
        freq[c] = freq.get(c, 0) + 1

    # Try PostgreSQL first
    if HAS_POSTGRES:
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'bincom_test')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_pass = os.environ.get('DB_PASSWORD', '')

        try:
            conn = psycopg2.connect(
                host=db_host, port=db_port, dbname=db_name,
                user=db_user, password=db_pass
            )
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS color_frequency (
                    id SERIAL PRIMARY KEY,
                    color VARCHAR(50),
                    frequency INT
                )
            """)
            cur.execute("TRUNCATE TABLE color_frequency RESTART IDENTITY")

            for color, count in freq.items():
                cur.execute(
                    "INSERT INTO color_frequency (color, frequency) VALUES (%s, %s)",
                    (color, count)
                )

            conn.commit()
            cur.execute("SELECT * FROM color_frequency ORDER BY frequency DESC")
            print("Saved to PostgreSQL:")
            for row in cur.fetchall():
                print(f"  {row[0]}: {row[1]} - {row[2]}")

            cur.close()
            conn.close()
            print(">>> PostgreSQL saved successfully")
            return True

        except Exception as e:
            print(f"PostgreSQL failed: {e}")

    # Fallback to SQLite
    print("Using SQLite fallback...")
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colors.db')
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS color_frequency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT,
            frequency INTEGER
        )
    """)
    cur.execute("DELETE FROM color_frequency")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='color_frequency'")

    for color, count in freq.items():
        cur.execute(
            "INSERT INTO color_frequency (color, frequency) VALUES (?, ?)",
            (color, count)
        )

    conn.commit()
    cur.execute("SELECT * FROM color_frequency ORDER BY frequency DESC")
    print("Saved to SQLite:")
    for row in cur.fetchall():
        print(f"  ID {row[0]}: {row[1]} - {row[2]}")

    cur.close()
    conn.close()
    print(">>> Database saved successfully")
    return True


# Q7: Recursive Binary Search
def binary_search(arr, target, left=0, right=None):
    """Recursive binary search. Returns (found, index)."""
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


def run_search():
    """Interactive binary search."""
    print("\nQ7: RECURSIVE BINARY SEARCH")
    print("-" * 40)

    nums = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29,
            31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59,
            61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89,
            91, 93, 95, 97, 99]

    print(f"List: {nums}")
    print(f"(Odd numbers 1-99)")

    try:
        val = input("Enter number to search: ")
        target = int(val)
        found, idx = binary_search(nums, target)

        if found:
            print(f">>> Found {target} at index {idx}")
        else:
            print(f">>> {target} not found in the list")
    except ValueError:
        print("Invalid input")


# Q8: Binary to Decimal
def binary_convert():
    """Generate random 4-digit binary and convert to decimal."""
    print("\nQ8: BINARY TO DECIMAL")
    print("-" * 40)

    binary = ''.join(str(random.randint(0, 1)) for _ in range(4))
    decimal = int(binary, 2)

    print(f"Generated: {binary}")
    print(f">>> Binary {binary} = Decimal {decimal}")
    return binary, decimal


# Q9: Fibonacci Sum
def fib_sum(n=50):
    """Sum of first n Fibonacci numbers."""
    print("\nQ9: FIBONACCI SUM")
    print("-" * 40)

    a, b = 0, 1
    total = 0
    fibs = []

    for _ in range(n):
        fibs.append(a)
        total += a
        a, b = b, a + b

    print(f"First 10: {fibs[:10]}")
    print(f">>> Sum of first {n} Fibonacci numbers: {total}")
    return total


def main():
    print("=" * 50)
    print("BINCOM DEVELOPER TEST")
    print("=" * 50)

    # Get data
    print("\nFetching data...")
    colors = get_color_data()

    if not colors:
        print("Using sample data...")
        colors = sample_colors()

    print(f"Loaded {len(colors)} color entries\n")

    # Run all questions
    mean_color(colors)
    mode_color(colors)
    median_color(colors)
    variance(colors)
    prob_red(colors)
    save_to_db(colors)
    run_search()
    binary_convert()
    fib_sum()

    print("\n" + "=" * 50)
    print("DONE")
    print("=" * 50)


if __name__ == "__main__":
    main()