# Gaming Zone API & Telegram Admin

სათამაშო სივრცის მოწყობილობების სტატუსების მართვის პროტოტიპი.

FastAPI read API with an aiogram admin interface for PC/PS5 availability.

## Implemented behavior

- `GET /api/v1/devices` groups devices into `pcs` and `ps5s`.
- `GET /api/v1/tournament/bracket` reads stored tournament matches.
- Telegram `/admin` lists devices and toggles `FREE` / `OCCUPIED` in SQLAlchemy.
- First database import creates tables and seeds 28 PCs and 28 PS5s if no devices exist.

## Local setup

```bash
git clone https://github.com/miqelius/gaming-zone-.git
cd gaming-zone-
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

```bash
cp .env.example .env
# Set BOT_TOKEN and ADMIN_USERNAME; omit the @ in the username.
uvicorn main:app --env-file .env --reload
```

Open http://127.0.0.1:8000/docs. Startup also launches Telegram long polling; use one worker for local testing.

| Variable | Purpose |
| --- | --- |
| `BOT_TOKEN` | Required Telegram bot token |
| `ADMIN_USERNAME` | Telegram username permitted to use admin actions |
| `DATABASE_URL` | Optional; defaults to `sqlite:///./gaming_zone.db` |

## Try the flow

Call `/api/v1/devices`, send `/admin` from the configured account, toggle one device, and call the API again. The changed status should persist after restarting the process.

## Limits

Tournament matches are read-only through this API; there is no match creation endpoint, booking system, timer, or payment flow. Admin access compares a mutable username rather than a numeric Telegram ID. Polling task shutdown and concurrent updates need hardening before a shared deployment. Dependencies are not locked; no automated tests are included.

## Source map

`main.py`: API, bot handlers, lifespan. `database.py`: connection, models, initial seed.

## Verification scope

Documentation was checked against the default-branch source on 2026-11-08. Source inspection and Python syntax checks do not establish a working deployment. External services, credentials, and live data were not exercised.
