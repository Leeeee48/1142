import requests
import sqlite3

DB_FILE = "data_collection.db"
ORG_NAME = "microsoft"
API_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"


def create_repo_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS github_repos (
        id INTEGER PRIMARY KEY,
        repo_name TEXT NOT NULL,
        full_name TEXT NOT NULL,
        description TEXT,
        html_url TEXT NOT NULL,
        stargazers_count INTEGER,
        forks_count INTEGER,
        language TEXT,
        source_org TEXT NOT NULL,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def fetch_repos():
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(API_URL, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json(), response.status_code


def save_repos(repos):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for repo in repos:
        cursor.execute(
            """
            INSERT OR REPLACE INTO github_repos (
                id, repo_name, full_name, description, html_url,
                stargazers_count, forks_count, language, source_org
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                repo["id"],
                repo["name"],
                repo["full_name"],
                repo["description"],
                repo["html_url"],
                repo["stargazers_count"],
                repo["forks_count"],
                repo["language"],
                ORG_NAME,
            ),
        )

    conn.commit()
    conn.close()


def main():
    create_repo_table()
    repos, status_code = fetch_repos()
    save_repos(repos)

    print(f"成功抓取 {len(repos)} 筆 {ORG_NAME} 公開 repositories，HTTP {status_code}")


if __name__ == "__main__":
    main()
