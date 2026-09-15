# PTT Ticket Alert Bot

A lightweight real-time monitoring service for Taiwan's PTT Drama-Ticket board. It polls the board's RSS feed, retrieves article content, optionally filters posts by keywords, and sends matching ticket alerts to Telegram.

## Features

- Monitor the PTT Drama-Ticket RSS feed automatically
- Scrape article content with Requests and BeautifulSoup
- Optional keyword filtering through an environment variable
- Avoid duplicate notifications during the current process lifetime
- Send alerts through the Telegram Bot API
- Configurable polling interval
- Health endpoint for deployment monitoring
- Deploy with Flask, Gunicorn, and Render

## Architecture

```text
PTT Drama-Ticket
       |
       v
    RSS Feed
       |
       v
  feedparser
       |
       v
Article Retrieval
Requests + BeautifulSoup
       |
       v
 Optional Keyword Filter
       |
       v
 In-memory Deduplication
       |
       v
 Telegram Bot API
```

## Tech Stack

- Python 3.11
- Flask
- Requests
- Feedparser
- BeautifulSoup4
- Gunicorn
- Telegram Bot API
- Render

## Project Structure

```text
.
├── app.py              # Application and RSS monitoring logic
├── render.yaml         # Render deployment configuration
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Poetry project configuration
├── poetry.lock         # Locked Poetry dependencies
├── .gitignore
└── README.md
```

## How It Works

1. Poll the PTT Drama-Ticket RSS feed.
2. Skip posts already processed during the current session.
3. Fetch and parse each new article.
4. Apply keyword filtering when `KEYWORDS` is configured.
5. Build a short article preview.
6. Send matching posts to Telegram.

## Configuration

Configure the application with environment variables. API tokens and credentials should never be committed to the repository.

| Variable | Required | Description |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Yes | Destination chat ID |
| `KEYWORDS` | No | Comma-separated keywords; empty means send all posts |
| `POLL_INTERVAL` | No | RSS polling interval in seconds; default is `30` |
| `PTT_RSS_URL` | No | RSS source URL |

Example keyword configuration:

```text
KEYWORDS=五月天,讓票,徵票,mayday
```

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the required environment variables and start the service:

```bash
gunicorn app:app
```

The application exposes:

- `/` — service status and configured keyword filter
- `/health` — lightweight health check

## Deployment

`render.yaml` contains the Render web-service configuration. The deployed service runs with:

```bash
gunicorn app:app
```

## Current Limitations

- Processed URLs are stored in memory and reset after a restart.
- The RSS monitor runs in a background thread inside the web process.
- Multiple Gunicorn workers could create duplicate monitoring loops.

## Future Improvements

- Persist processed posts with Redis or a database
- Move RSS monitoring to a dedicated background worker
- Add automated tests and CI
- Extract structured fields such as event, date, venue, quantity, and price
- Build analytics for ticket-post volume and trends
- Apply NLP for post classification and information extraction

## Author

Yu-shan Huang
