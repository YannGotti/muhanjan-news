# MuhanjanNews / MuhanjanLoto Production (без Docker)

Полностью переделанный проект под поток:

1. Пользователь пишет в Telegram-бота.
2. При первом входе обязательно указывает Twitch-ник.
3. Отправляет текст, ссылки, фото и файлы.
4. Предложка попадает в backend.
5. Модератор открывает ПК-панель на Vue и одобряет / отклоняет / банит.
6. После одобрения запись видна на отдельной странице для стримера.
7. Админ может включать и выключать режим модерации.

## Домены
- Фронт: `muhanjanloto.void-rp.ru`
- Бэкенд: `muhanjanloto.api.void-rp.ru`

## Порты
- Ваш текущий VOIDRP API: `8001` (не трогаем)
- MuhanjanNews API: `8002`
- Frontend dev: `5174`

## Структура
- `apps/api` — FastAPI + PostgreSQL + SQLAlchemy + Alembic
- `apps/bot` — Telegram bot на aiogram
- `apps/web` — Vue 3 + Vite + Tailwind + Pinia + Vue Router
- `deploy/nginx` — готовые nginx-конфиги
- `deploy/systemd` — systemd unit-файлы
- `storage/uploads` — локальное хранилище файлов

---

## 1. PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE USER muhanjannews WITH PASSWORD 'strong_password_here';
CREATE DATABASE muhanjannews OWNER muhanjannews;
GRANT ALL PRIVILEGES ON DATABASE muhanjannews TO muhanjannews;
\q
```

---

## 2. Backend

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

Заполни `.env`, затем:

```bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Проверка:

```bash
curl http://127.0.0.1:8002/health
```

---

## 3. Bot

```bash
cd apps/bot
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

---

## 4. Frontend

```bash
cd apps/web
cp .env.example .env
npm install
npm run build
```

Выложить сборку:

```bash
sudo mkdir -p /var/www/muhanjannews/web
sudo cp -r dist/* /var/www/muhanjannews/web/
```

Локальная разработка:

```bash
npm run dev -- --host 0.0.0.0 --port 5174
```

---

## 5. Nginx

Смотри файл `deploy/nginx/muhanjanloto.conf`.

Он уже сделан так, чтобы:
- не ломать существующий `void-rp.ru`
- не ломать `api.void-rp.ru -> 127.0.0.1:8001`
- повесить новый фронт на `muhanjanloto.void-rp.ru`
- повесить новый backend на `muhanjanloto.api.void-rp.ru -> 127.0.0.1:8002`

После копирования:

```bash
sudo cp deploy/nginx/muhanjanloto.conf /etc/nginx/sites-available/muhanjanloto.conf
sudo ln -s /etc/nginx/sites-available/muhanjanloto.conf /etc/nginx/sites-enabled/muhanjanloto.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

## 6. Certbot

Если поддомены ещё не выпущены в сертификат:

```bash
sudo certbot --nginx -d muhanjanloto.void-rp.ru -d muhanjanloto.api.void-rp.ru
```

Если используется уже существующий wildcard или SAN-сертификат — просто замени пути в nginx при необходимости.

---

## 7. systemd

### Backend

```bash
sudo cp deploy/systemd/muhanjannews-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now muhanjannews-api
```

### Bot

```bash
sudo cp deploy/systemd/muhanjannews-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now muhanjannews-bot
```

---

## 8. Что умеет проект

### Telegram bot
- обязательная привязка Twitch-ника
- приём текста
- извлечение ссылок из текста
- приём фото
- приём документов
- бан пользователя
- блокировка отправки без Twitch-ника

### Backend
- JWT auth для web-панели
- users / submissions / attachments / settings / moderation actions
- хранение файлов локально
- переключатель `moderation_enabled`
- если модерация выключена — записи сразу идут в approved

### Web
- страница логина
- панель модератора
- список pending / approved / rejected
- approve / reject / ban
- страница стримера с approved
- переключатель режима модерации

---

## 9. Что обязательно заполнить

### `apps/api/.env`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `BASE_PUBLIC_API_URL=https://muhanjanloto.api.void-rp.ru`
- `BASE_PUBLIC_WEB_URL=https://muhanjanloto.void-rp.ru`

### `apps/bot/.env`
- `BOT_TOKEN`
- `API_BASE_URL=https://muhanjanloto.api.void-rp.ru`

### `apps/web/.env`
- `VITE_API_BASE_URL=https://muhanjanloto.api.void-rp.ru`

---

## 10. Полезные маршруты

- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/admin/submissions`
- `POST /api/v1/admin/submissions/{id}/approve`
- `POST /api/v1/admin/submissions/{id}/reject`
- `POST /api/v1/admin/users/{id}/ban`
- `GET /api/v1/stream/feed`
- `GET /api/v1/settings/public`

---

## 11. Быстрая проверка после запуска

1. Запусти API и бота.
2. Напиши боту `/start`.
3. Укажи Twitch-ник.
4. Отправь текст + ссылку.
5. Открой `https://muhanjanloto.void-rp.ru/login`.
6. Войди логином и паролем из `.env` backend.
7. Проверь approve / reject / ban.
8. Открой `https://muhanjanloto.void-rp.ru/stream`.

---

## 12. Замечания

Это production-ready каркас: архитектура, миграции, backend, bot, web, nginx, systemd. Под боевой сервер тебе останется:
- поставить реальные секреты
- выдать сертификаты
- убедиться в правах на `/var/www/muhanjannews` и `storage/uploads`
- при желании добавить websocket / SSE и очередь “следующая новость”
# muhanjan-news
