# MuhanjanNews Bot

Новая структура Telegram-бота:

- `bot.py` — совместимая точка входа для старого запуска
- `main.py` — экспорт функции запуска
- `muhanjan_bot/config.py` — конфиг и переменные окружения
- `muhanjan_bot/app.py` — сборка бота и запуск polling
- `muhanjan_bot/handlers/` — обработчики команд, профиля и отправки материалов
- `muhanjan_bot/services/` — API, загрузка файлов и работа с пользователем
- `muhanjan_bot/keyboards/` — reply-клавиатуры
- `muhanjan_bot/states/` — FSM состояния
- `muhanjan_bot/texts.py` — все тексты для пользователя

## Запуск

```bash
cd apps/bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

## Что умеет бот

- понятный старт и меню
- кнопки с быстрыми действиями
- отдельный сценарий для ввода Twitch-ника
- просмотр статуса пользователя
- смена Twitch-ника
- подсказки по формату отправки
- приём текста, ссылок, фото, документов и видео
- понятные ответы при ошибках API и ограничениях
