import csv
import json
import sqlite3

from .models import Topic

SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    ref TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    skills TEXT NOT NULL,
    duration_min INTEGER,
    duration_max INTEGER,
    places INTEGER
)
"""


def connect(path):
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    return conn


def replace_topics(path, topics):
    conn = connect(path)
    try:
        with conn:
            conn.execute("DELETE FROM topics")
            conn.executemany(
                "INSERT INTO topics VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        t.ref,
                        t.title,
                        t.text,
                        json.dumps(t.skills, ensure_ascii=False),
                        t.duration_min,
                        t.duration_max,
                        t.places,
                    )
                    for t in topics
                ],
            )
    finally:
        conn.close()
    return len(topics)


def load_topics(path):
    conn = connect(path)
    try:
        rows = conn.execute(
            "SELECT ref, title, text, skills, duration_min, duration_max, places "
            "FROM topics ORDER BY ref"
        ).fetchall()
    finally:
        conn.close()
    return [
        Topic(r[0], r[1], r[2], json.loads(r[3]), r[4], r[5], r[6]) for r in rows
    ]


def export_csv(topics, target):
    with open(target, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["ref", "title", "skills", "duration_min", "duration_max", "places"]
        )
        for t in topics:
            writer.writerow(
                [t.ref, t.title, ", ".join(t.skills), t.duration_min, t.duration_max, t.places]
            )
    return len(topics)
