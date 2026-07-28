# bookclubbot

Posts the day's book club reading to a Discord channel automatically, once a day at 08:00 Europe/Oslo time. No always-on bot or server required — a GitHub Actions workflow runs the script every hour, and the script itself decides whether it's the right local hour and whether there's anything scheduled for today.

## Setup

1. **Create a Discord webhook**: in the target channel, go to Edit Channel → Integrations → Webhooks → New Webhook, then copy the webhook URL.
2. **Add it as a GitHub secret**: in this repo on GitHub, go to Settings → Secrets and variables → Actions → New repository secret, name it `DISCORD_WEBHOOK_URL`, and paste the URL.
3. Push this repo to GitHub. The `daily-post.yml` workflow will start running automatically on its hourly schedule.

## Starting a new book

Each reading period is its own file under `books/`. To start a new book, add a new YAML file (e.g. `books/2026-09-my-new-book.yaml`) with its own dates and push — no code changes or edits to existing files needed:

```yaml
book: "New Book Title"
schedule:
  2026-09-01: "Chapter 1"
  2026-09-02: "Chapter 2"
```

Every file in `books/` is scanned each run; the script posts whichever entry matches today's date. Dates with no entry in any file are silently skipped. If two files both have an entry for the same date (e.g. overlapping periods), the run fails loudly (visible as a red X in the Actions tab) instead of guessing which one to post — fix the overlap and it'll pick back up on the next hourly run.

## Testing locally

```bash
pip install -r requirements.txt
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python post_reading.py
```

Note the script only posts at 08:00 local (Europe/Oslo) time — for a local test outside that hour, temporarily change `POST_HOUR` in `post_reading.py` or add a plan entry and run at 08:00.

## Testing the GitHub Actions workflow

Use the "Run workflow" button on the Actions tab (enabled via `workflow_dispatch`) to trigger a manual run without waiting for the schedule.
