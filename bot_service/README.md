# Bot Service (testable)

## Run tests
```bash
python -m pip install -r bot_service/requirements.txt
pytest -q bot_service/tests
```

## Run bot (polling)
```bash
export BOT_TOKEN=<telegram_bot_token>
export WEBAPP_URL=https://your-mini-app.example
python -m bot_service.bot.main
```
