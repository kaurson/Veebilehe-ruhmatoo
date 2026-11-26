import sqlite3
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "rss_database.db"


async def get_articles(limit: int = 5, offset: int = 0): # asünkroonne funktsioon, mis tagastab x number artikleid andmebaasist, alates offset-ist
  async with aiosqlite.connect(DB_PATH) as db: # ühendame andmebaasiga
        db.row_factory = aiosqlite.Row # loome row factory'i
        async with db.execute(
            "SELECT id, title, published, source, link FROM articles ORDER BY id DESC LIMIT ? OFFSET ?", 
            (limit, offset) # valime andmebaasist x number artikleid, alates offset-ist
        ) as cursor:
            rows = await cursor.fetchall() # salvestame andmed muutujasse
            return [dict(row) for row in rows] # tagastame x number artikleid andmebaasist






async def get_recent_articles(scan: int = 50): # tagastab viimased scan artiklit (kategoriseerimiseks)
  return await get_articles(scan, 0)


async def get_article_by_id(article_id): # asünkroonne funktsioon, mis tagastab artikli andmed andmebaasist
  conn = sqlite3.connect(DB_NAME) # ühendame andmebaasiga
  cursor = conn.cursor() # loome cursori
  cursor.execute(
      """
        SELECT id, source, title, published, link, summary
        FROM articles
        WHERE id = ?
      """
    ) # Teeme käsu, mis valib andmebaasist artikli andmed
  article = cursor.fetchone() # salvestame andmed muutujasse
  conn.close() # sulgeme andmebaasiga ühenduse
  return article # tagastame andmed





