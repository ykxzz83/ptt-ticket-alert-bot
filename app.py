import logging
import os
import threading
import time

import feedparser
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

RSS_URL = os.getenv("PTT_RSS_URL", "https://www.ptt.cc/atom/Drama-Ticket.xml")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))
KEYWORDS = [
    keyword.strip().lower()
    for keyword in os.getenv("KEYWORDS", "").split(",")
    if keyword.strip()
]

REQUEST_TIMEOUT = 10
PREVIEW_LENGTH = 200
sent_links: set[str] = set()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_article_content(link: str) -> str:
    """Fetch and extract the main text from a PTT article."""
    try:
        response = requests.get(
            link,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("div", id="main-content")
        return content.get_text(" ", strip=True) if content else ""
    except requests.RequestException as exc:
        logger.warning("Failed to fetch article %s: %s", link, exc)
        return ""


def matches_keywords(title: str, content: str) -> bool:
    """Return True when no filter is configured or a keyword is matched."""
    if not KEYWORDS:
        return True

    text = f"{title} {content}".lower()
    return any(keyword in text for keyword in KEYWORDS)


def send_telegram_message(text: str) -> bool:
    """Send an alert through the Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram credentials are not configured.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error("Failed to send Telegram alert: %s", exc)
        return False


def process_feed() -> None:
    """Process one snapshot of the configured RSS feed."""
    feed = feedparser.parse(RSS_URL)

    if getattr(feed, "bozo", False):
        logger.warning("RSS parser reported an issue: %s", feed.bozo_exception)

    for entry in feed.entries:
        title = entry.title.strip()
        link = entry.link

        if link in sent_links:
            continue

        content = fetch_article_content(link)

        if not matches_keywords(title, content):
            sent_links.add(link)
            continue

        preview = content[:PREVIEW_LENGTH]
        if len(content) > PREVIEW_LENGTH:
            preview += "..."

        message = f"📌 {title}\n\n📝 {preview}\n\n🔗 {link}"

        if send_telegram_message(message):
            sent_links.add(link)
            logger.info("Alert sent: %s", title)


def monitor_rss() -> None:
    """Continuously poll the RSS feed for new ticket posts."""
    logger.info("PTT ticket monitor started. Poll interval: %s seconds", POLL_INTERVAL)

    while True:
        try:
            process_feed()
        except Exception:
            logger.exception("Unexpected error while processing RSS feed")

        time.sleep(POLL_INTERVAL)


@app.get("/")
def home():
    return jsonify(
        status="ok",
        service="ptt-ticket-alert-bot",
        keyword_filter=KEYWORDS,
    )


@app.get("/health")
def health():
    return jsonify(status="healthy")


# Start one background monitor for the current application process.
monitor_thread = threading.Thread(target=monitor_rss, daemon=True, name="rss-monitor")
monitor_thread.start()
