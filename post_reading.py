import json
import os
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

TIMEZONE = ZoneInfo("Europe/Oslo")
POST_HOUR = 8
PLAN_PATH = os.path.join(os.path.dirname(__file__), "plan.yaml")


def load_plan():
    with open(PLAN_PATH, "r") as f:
        return yaml.safe_load(f)


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

    plan = load_plan()
    today = now.date()
    entry = plan.get("schedule", {}).get(today)
    if entry is None:
        print(f"No reading scheduled for {today}, skipping.")
        return

    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    message = f"\U0001f4d6 **{plan['book']}** — today's reading: {entry}"
    post_to_discord(webhook_url, message)
    print(f"Posted: {message}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
