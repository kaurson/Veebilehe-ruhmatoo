from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import sqlite3
from queery_db import get_article_by_id, get_articles as fetch_articles, get_recent_articles
from pathlib import Path
from starlette.concurrency import run_in_threadpool
from inference import classify



# GLOBAL VARIABLES
DB_PATH = "rss_database.db"
STATIC_DIR = Path(__file__).resolve().parent.parent / "html" / "static"

app = FastAPI() # Initsialiseerin FastAPI


@app.get("/articles/{article_id}") # Get request, mis tagastab artikli andmed andmebaasist
async def get_article(article_id: int):
    article = get_article_by_id(article_id)
    return article


@app.get("/articles/{limit}/{offset}") # Get request, mis tagastab x number artikleid andmebaasist, alates offset-ist
async def get_articles(limit: int = 5, offset: int = 0):
    articles = await fetch_articles(limit, offset)
    return articles 

@app.get("/classify")
async def classify_article(title: str, summary: str):
    return classify(title, summary)


SCAN_LIMIT = 50 # mitu viimast artiklit kategoriseerimiseks läbi vaadatakse

@app.get("/categorised-feed") # Tagastab artiklid, mis sobivad valitud kategooriatega
async def categorised_feed(categories: str, limit: int = 5):
    names = [c.strip() for c in categories.split(",") if c.strip()]
    if len(names) < 2:
        raise HTTPException(status_code=400, detail="Lisa vähemalt 2 kategooriat")
    matches = []
    for article in await get_recent_articles(SCAN_LIMIT):
        result = await run_in_threadpool(classify, article["title"], None, names)
        if result["choice"] in names:
            matches.append(article)
            if len(matches) >= limit:
                break
    return matches


# Loome static kataloogi, kui see ei ole olemas
#STATIC_DIR.mkdir(exist_ok=True)

class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


# Mountime static kataloogi
app.mount("/", NoCacheStaticFiles(directory=STATIC_DIR, html=True), name="static")

# Startime FastAPI serveri
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)