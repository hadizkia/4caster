# 4caster

A Telegram bot that draws weather-forecast maps and charts on request, running entirely on GitHub Actions.

- Users ask in plain language; a free-tier LLM turns the request into either ready-made map settings or a short
  plotting script, which runs in a sandbox (separate user, no secrets, time limit).
- Forecast data: [Open-Meteo](https://open-meteo.com) (CC BY 4.0), several global models and ensembles.
- Farm forecasts: frost and heat probabilities from ensembles, crop water need (FAO-56), spraying windows,
  soil conditions, degree-days and chill hours, regional frost and water-need maps, and daily alerts.
- Every 5 minutes the workflow checks the bot for new messages and answers them; once a day it refreshes the
  model data. State and data live in the Actions cache; the state is encrypted.
- Only users approved by the admin can use the bot.

The application code and assets are kept in an encrypted bundle (`bundle.bin`), unpacked at run time by `run.py`
with the `BUNDLE_KEY` secret. `pack.py` builds the bundle.

## Secrets
`TELEGRAM_BOT_TOKEN`, `ADMIN_ID`, `ALLOWED_IDS` (comma list, may be empty), `STATE_KEY` (random string),
`LLM_API_KEY`, `BUNDLE_KEY`. Optional repository variable `LLM_MODELS`.
