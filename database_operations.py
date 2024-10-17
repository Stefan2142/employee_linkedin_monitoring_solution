import sqlite3
import pandas as pd
from datetime import datetime


def init_db():
    conn = sqlite3.connect("linkedin_data.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS profile_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date_time TEXT,
                  profile_url TEXT,
                  interests_count INTEGER,
                  skills_count INTEGER,
                  status TEXT)"""
    )
    conn.commit()
    conn.close()


def insert_profile_data(date_time, profile_url, interests_count, skills_count, status):
    conn = sqlite3.connect("linkedin_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO profile_data (date_time, profile_url, interests_count, skills_count, status) VALUES (?, ?, ?, ?, ?)",
        (date_time, profile_url, interests_count, skills_count, status),
    )
    conn.commit()
    conn.close()


def get_previous_week_data():
    conn = sqlite3.connect("linkedin_data.db")
    c = conn.cursor()
    c.execute(
        "SELECT profile_url, interests_count, skills_count FROM profile_data WHERE date_time = (SELECT MAX(date_time) FROM profile_data WHERE date_time < date('now', '-7 days'))"
    )
    data = c.fetchall()
    conn.close()
    return {row[0]: {"interests": row[1], "skills": row[2]} for row in data}


def generate_comparison_report(current_data, previous_data):
    report = []
    for profile_url, current_counts in current_data.items():
        if profile_url in previous_data:
            prev_counts = previous_data[profile_url]
            interests_diff = current_counts["interests"] - prev_counts["interests"]
            skills_diff = current_counts["skills"] - prev_counts["skills"]
            report.append(f"Profile: {profile_url}")
            report.append(f"Interests change: {interests_diff}")
            report.append(f"Skills change: {skills_diff}")
            report.append("---")
    return "\n".join(report)


def get_all_data_for_visualization():
    conn = sqlite3.connect("linkedin_data.db")
    query = """
    SELECT date_time, profile_url, interests_count, skills_count
    FROM profile_data
    ORDER BY date_time DESC, profile_url
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
