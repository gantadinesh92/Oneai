from __future__ import annotations

import datetime as dt
import json
import os
import sqlite3
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable, List

DB_PATH = os.getenv("STOCK_NEWS_DB_PATH", "stock_news.db")
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
TOP_COMPANIES = ["Apple", "Microsoft", "Amazon", "Alphabet", "NVIDIA"]


@dataclass
class NewsArticle:
    company: str
    title: str
    link: str
    published_at: str


def _connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            UNIQUE(company, link)
        )
        """
    )
    conn.commit()
    return conn


def _google_news_url(company: str) -> str:
    query = f"{company} stock"
    encoded = urllib.parse.urlencode({"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    return f"{GOOGLE_NEWS_RSS}?{encoded}"


def _fetch_feed(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.read()


def _parse_articles(feed_xml: bytes, company: str, limit: int = 10) -> List[NewsArticle]:
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")
    if channel is None:
        return []

    articles: List[NewsArticle] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        published_at = (item.findtext("pubDate") or "").strip()
        if title and link:
            articles.append(
                NewsArticle(company=company, title=title, link=link, published_at=published_at)
            )

    return articles


def _save_articles(conn: sqlite3.Connection, articles: Iterable[NewsArticle]) -> int:
    fetched_at = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    inserted = 0
    for article in articles:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO stock_news (company, title, link, published_at, fetched_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (article.company, article.title, article.link, article.published_at, fetched_at),
        )
        if cursor.rowcount:
            inserted += 1

    conn.commit()
    return inserted


def update_stock_news(companies: Iterable[str] = TOP_COMPANIES, db_path: str = DB_PATH) -> dict:
    conn = _connect(db_path)
    per_company = {}
    total_inserted = 0

    try:
        for company in companies:
            url = _google_news_url(company)
            feed_xml = _fetch_feed(url)
            articles = _parse_articles(feed_xml, company)
            inserted = _save_articles(conn, articles)
            per_company[company] = {"fetched": len(articles), "inserted": inserted}
            total_inserted += inserted
    finally:
        conn.close()

    return {
        "status": "ok",
        "companies": list(companies),
        "inserted": total_inserted,
        "details": per_company,
        "updated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }


def cli() -> int:
    result = update_stock_news()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
