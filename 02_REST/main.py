import requests
import sqlite3

DB_FILE = "data_collection.db"
API_URL = "https://jsonplaceholder.typicode.com/posts"


def create_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        source_type TEXT NOT NULL,
        base_url TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        method TEXT NOT NULL DEFAULT 'GET',
        requires_auth INTEGER NOT NULL DEFAULT 0,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fetch_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status_code INTEGER,
        record_count INTEGER,
        success INTEGER NOT NULL,
        message TEXT,
        FOREIGN KEY (source_id) REFERENCES data_sources(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        source_id INTEGER NOT NULL,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES data_sources(id)
    )
    """)

    conn.commit()
    conn.close()


def register_source():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO data_sources (
            source_name, source_type, base_url, endpoint, method, requires_auth, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "JSONPlaceholder Posts",
            "website_mock_api",
            "https://jsonplaceholder.typicode.com",
            "/posts",
            "GET",
            0,
            "Practice API for collecting website-like post data",
        ),
    )

    source_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return source_id


def fetch_posts():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response


def save_posts(posts, source_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for post in posts:
        cursor.execute(
            """
            INSERT OR REPLACE INTO posts (id, user_id, title, body, source_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (post["id"], post["userId"], post["title"], post["body"], source_id),
        )

    conn.commit()
    conn.close()


def write_log(source_id, status_code, record_count, success, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO fetch_logs (source_id, status_code, record_count, success, message)
        VALUES (?, ?, ?, ?, ?)
        """,
        (source_id, status_code, record_count, success, message),
    )

    conn.commit()
    conn.close()


def main():
    create_tables()
    source_id = register_source()

    try:
        response = fetch_posts()
        posts = response.json()
        save_posts(posts, source_id)
        write_log(
            source_id, response.status_code, len(posts), 1, "Posts fetched successfully"
        )
        print(f"成功下載並存入 {len(posts)} 筆文章資料")
    except Exception as e:
        write_log(source_id, None, 0, 0, str(e))
        print("資料擷取失敗：", e)


if __name__ == "__main__":
    main()
