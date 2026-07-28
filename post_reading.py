import glob
import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

TIMEZONE = ZoneInfo("Europe/Oslo")
POST_HOUR = 8
BOOKS_DIR = os.path.join(os.path.dirname(__file__), "books")


def load_books():
    books = []
    for path in sorted(glob.glob(os.path.join(BOOKS_DIR, "*.yaml"))):
        with open(path, "r") as f:
            books.append((path, yaml.safe_load(f)))
    return books


def find_todays_entry(books, today):
    matches = []
    for path, book in books:
        entry = book.get("schedule", {}).get(today)
        if entry is not None:
            matches.append((path, book, entry))

    if len(matches) > 1:
        matching_paths = ", ".join(path for path, _, _ in matches)
        raise RuntimeError(
            f"Multiple book files have an entry for {today}: {matching_paths}"
        )

    return matches[0] if matches else None


def post_to_discord(webhook_url, message):
    body = json.dumps({"content": message}).encode()
    request = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        if response.status >= 300:
            raise RuntimeError(f"Discord webhook returned status {response.status}")


def main():
    now = datetime.now(TIMEZONE)
    if now.hour != POST_HOUR:
        print(f"Not post hour (local hour {now.hour}), skipping.")
        return

    today = now.date()
    books = load_books()
    match = find_todays_entry(books, today)
    if match is None:
        print(f"No reading scheduled for {today}, skipping.")
        return

    _, _book, entry = match
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    message = entry
    post_to_discord(webhook_url, message)
    print(f"Posted: {message}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
