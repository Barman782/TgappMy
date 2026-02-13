# Bot Service (testable)

## Быстрый запуск (локально)

1. Создайте и активируйте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:
```bash
python -m pip install -r bot_service/requirements.txt
```

3. Укажите переменные окружения:
```bash
export BOT_TOKEN='<ваш_токен_бота>'
export WEBAPP_URL='https://your-mini-app.example'
```

4. Запустите бота:
```bash
python -m bot_service.bot.main
```

Если запуск успешный, бот начнет polling и будет отвечать в Telegram.

---

## Проверка тестов
```bash
pytest -q bot_service/tests
```

---

## Как проверить в Telegram

1. Откройте чат с вашим ботом.
2. Нажмите **Start** или отправьте `/start`.
3. В сообщении появится кнопка запуска Mini App (WEBAPP_URL).

---

## Частые проблемы

### 1) `Network is unreachable` / нет доступа к `api.telegram.org`
Окружение, где запущен бот, не имеет исходящего доступа в интернет к Telegram API. Запустите на VPS/сервере с открытым outbound доступом.

### 2) Бот не отвечает
Проверьте:
- что токен корректный;
- что процесс запущен без ошибок;
- что не запущен второй экземпляр polling с тем же токеном.

### 3) Кнопка Mini App не открывается
Убедитесь, что `WEBAPP_URL` — валидный HTTPS URL.

---

## Запуск бота через GitHub Actions

Добавлен workflow: `.github/workflows/run-bot.yml`.

1. Откройте репозиторий на GitHub → **Settings → Secrets and variables → Actions**.
2. Добавьте secrets:
   - `BOT_TOKEN` — токен Telegram-бота;
   - `WEBAPP_URL` — HTTPS URL вашего Mini App.
3. Откройте вкладку **Actions** → workflow **Run Telegram Bot (manual)**.
4. Нажмите **Run workflow**.

> Важно: GitHub Actions не подходит для постоянного 24/7 polling.
> Job ограничен по времени (в workflow выставлено `timeout-minutes: 360`).
> Для постоянной работы бота используйте VPS/Cloud Run/Render/Fly.io.
