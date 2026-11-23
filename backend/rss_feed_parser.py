from datetime import datetime
import sqlite3
import time
import feedparser
from newspaper import Article

ARTICLES_PER_FEED = 10
REQUEST_DELAY_SECONDS = 2

DB_NAME = "../rss_database.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            published TEXT,
            summary TEXT,
            full_text TEXT,
            source TEXT,
            author TEXT
        )
    """
  )
  existing = {row[1] for row in cursor.execute("PRAGMA table_info(articles)")}
  for column in ("full_text", "author"):
    if column not in existing:
      cursor.execute(f"ALTER TABLE articles ADD COLUMN {column} TEXT")
  conn.commit()
  conn.close()


def purge_db():
  init_db()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM articles")
  cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'articles'")
  conn.commit()
  conn.close()
  print("Database purged. All articles removed.")


RSS_FEEDS = {
   "CNBC Top News": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNBC World": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    #"MarketWatch Top Stories": "https://feeds.marketwatch.com/marketwatch/topstories",
    #"Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
    #"FT Home": "https://www.ft.com/?format=rss",
    "FT Markets": "https://www.ft.com/markets?format=rss",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Forbes Business": "https://www.forbes.com/business/feed/",
    }


def fetch_and_store_rss():
  init_db()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  new_articles_count = 0

  for source_name, url in RSS_FEEDS.items():
    print(f"Fetching feed: {source_name}...")
    feed = feedparser.parse(url)

    for entry in feed.entries[:ARTICLES_PER_FEED]:
      title = entry.get("title", "No Title")
      link = entry.get("link", "")
      published = entry.get(
          "published", entry.get("updated", datetime.now().isoformat())
      )
      summary = entry.get("summary", entry.get("description", ""))
      author = entry.get("author", "Unknown")

      # Skip if link is missing or already in DB
      if not link:
        continue

      # Check if article already exists to avoid redundant web scraping
      cursor.execute("SELECT id FROM articles WHERE link = ?", (link,))
      if cursor.fetchone():
        continue

      full_text = None

      try:
        print(f"  -> Extracting full text for: {title[:30]}...")
        article = Article(link)
        article.download()
        article.parse()

        full_text = article.text  # Clean article text for your classifier

      except Exception as e:
        print(f"  -> Error downloading full text from {link}: {e}")
        full_text = summary  # Fallback to summary if scraping fails

      time.sleep(REQUEST_DELAY_SECONDS)

      try:
        cursor.execute(
            """
                    INSERT INTO articles (title, link, published, summary, full_text, source, author)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                title,
                link,
                published,
                summary,
                full_text,
                source_name,
                author,
            ),
        )
        new_articles_count += 1
      except Exception as e:
        print(f"Error saving to DB: {e}")

  conn.commit()
  conn.close()
  print(
      f"Sync complete! Processed and added {new_articles_count} new articles."
  )


if __name__ == "__main__":
  fetch_and_store_rss()