# Oneai stock news cron pulse

This project now supports an hourly cron pulse that invokes the Flask application to fetch the latest Google News headlines for stock data related to these top 5 companies:

- Apple
- Microsoft
- Amazon
- Alphabet
- NVIDIA

## How it works

1. GitHub Actions runs every hour (`0 * * * *`).
2. The workflow sends a `POST` request to `/tasks/update-stock-news`.
3. The application fetches Google News RSS results for each company.
4. New headlines are stored in a local SQLite database (`stock_news.db`) in table `stock_news`.

## App configuration

Set these environment variables in your runtime/deployment:

- `CRON_TOKEN`: Shared token used by the GitHub workflow and Flask endpoint.
- `STOCK_NEWS_DB_PATH` (optional): Override the default database path (`stock_news.db`).

## GitHub repository secrets

Configure these repository secrets:

- `APP_BASE_URL`: Public base URL for your deployed app (example: `https://my-app.example.com`).
- `CRON_TOKEN`: Same value configured in the app environment.

## Manual run

You can trigger the fetch/update manually:

```bash
python news_updater.py
```
