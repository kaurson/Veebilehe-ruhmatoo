from datetime import datetime
import sqlite3
import feedparser
from newspaper import Article

DB_NAME = "rss_database.db"


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
            image_url TEXT,
            full_text TEXT,
            source TEXT,
            author TEXT
        )
    """
  )
  conn.commit()
  conn.close()


RSS_FEEDS = {
    "Python Insider": "https://pyfound.blogspot.com/atom.xml",
    # Add more news feeds here
}


def fetch_and_store_rss():
  init_db()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  new_articles_count = 0

  for source_name, url in RSS_FEEDS.items():
    print(f"Fetching feed: {source_name}...")
    feed = feedparser.parse(url)

    for entry in feed.entries:
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

      image_url = None
      full_text = None

      # Extract full text and image using newspaper4k
      try:
        print(f"  -> Extracting full text for: {title[:30]}...")
        article = Article(link)
        article.download()
        article.parse()

        full_text = article.text  # Clean article text for your classifier
        image_url = article.top_image  # Main thumbnail image for your website

        # Fallback if feed has an image enclosure that newspaper missed
        if not image_url and "media_content" in entry:
          image_url = entry.media_content[0].get("url")

      except Exception as e:
        print(f"  -> Error downloading full text from {link}: {e}")
        full_text = summary  # Fallback to summary if scraping fails

      try:
        cursor.execute(
            """
                    INSERT INTO articles (title, link, published, summary, image_url, full_text, source, author)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
            (
                title,
                link,
                published,
                summary,
                image_url,
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