# PTT Ticket Alert Bot

A real-time ticket-post monitoring and notification bot for Taiwan's PTT Drama-Ticket board.

The application continuously reads the board's RSS feed, retrieves article content, and sends new ticket-post alerts through messaging platforms such as Telegram and LINE.

## Features

- Monitor the PTT Drama-Ticket RSS feed in near real time
- Retrieve and parse article content automatically
- Filter posts using configurable keywords
- Prevent duplicate notifications during a running session
- Send alerts through Telegram Bot API
- Support LINE Messaging API in the keyword-filtering version
- Deploy as a Flask web service with Gunicorn and Render

## How It Works

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
(requests + BeautifulSoup)
       |
       v
Keyword Filtering / Deduplication
       |
       v
Telegram / LINE Notification
```

## Tech Stack

- Python 3.11
- Flask
- Requests
- Feedparser
- BeautifulSoup4
- Gunicorn
- Telegram Bot API
- LINE Messaging API
- Render

## Project Structure

```text
.
├── app.py              # Main Telegram notification application
├── main_mayday.py      # Keyword-filtering LINE notification version
├── render.yaml         # Render deployment configuration
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Poetry project configuration
└── README.md
```

## Main Workflow

1. Poll the PTT Drama-Ticket RSS feed.
2. Detect posts that have not been processed during the current session.
3. Fetch each article page and extract its text content.
4. Create a short preview of the post.
5. Send the alert through the configured messaging API.
6. Record the article URL in memory to avoid duplicate alerts.

## Configuration

The application uses environment variables for messaging credentials. Do not commit API tokens or secrets to the repository.

For the Telegram version (`app.py`):

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

For the LINE version (`main_mayday.py`):

```text
LINE_CHANNEL_ACCESS_TOKEN
```

## Deployment

The project includes a `render.yaml` configuration for deployment on Render. The web service runs with:

```bash
gunicorn app:app
```

## Current Limitations

- Processed article URLs are stored only in memory, so the duplicate history is reset when the service restarts.
- Running multiple Gunicorn workers could start multiple monitoring threads.
- RSS polling and notification processing currently run inside the Flask application process.

Possible future improvements include persistent storage with Redis or a database, a dedicated background worker, configurable polling intervals, structured logging, and monitoring.

## Future Improvements

- Persist processed posts using Redis or a database
- Separate background monitoring from the Flask web server
- Add configurable keywords and polling intervals
- Extract structured ticket information such as event, date, venue, quantity, and price
- Add analytics and visualization for ticket-post trends
- Apply NLP models for ticket classification or suspicious-post detection

## Author

Sandy
