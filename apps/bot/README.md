# MuhanjanNews Bot

Согласованная версия Telegram-бота для MuhanjanNews.

## Что внутри

- Redis FSM
- shared httpx client
- антиспам на отправку
- защита от повторной отправки одного и того же сообщения
- глобальный обработчик ошибок
- совместимая точка входа `bot.py`

## Запуск

```bash
cd apps/bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Важно

После замены файлов желательно очистить `__pycache__` и перезапустить systemd-сервис.
