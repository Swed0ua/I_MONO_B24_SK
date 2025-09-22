# SmartKasa Integration

Інтеграція Monobank API "Покупка Частинами" з Bitrix24 CRM.

## Архітектура

- **FastAPI** - веб-фреймворк
- **PostgreSQL** - база даних
- **SQLAlchemy** - ORM
- **Redis** - кешування
- **Docker** - контейнеризація

## Структура проекту

```
app/
├── core/                   # Ядро системи
│   └── interfaces/         # Абстракції та інтерфейси
├── models/                 # Моделі БД
├── schemas/                # Pydantic схеми
├── services/               # Бізнес-логіка
├── repositories/           # Доступ до даних
├── api/v1/                 # API endpoints
├── webhooks/               # Обробка веб-хуків
└── utils/                  # Утиліти
```

## Встановлення

1. Клонуйте репозиторій
2. Створіть віртуальне середовище:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows
```

3. Встановіть залежності:
```bash
pip install -r requirements.txt
```

4. Скопіюйте `.env.example` в `.env` та налаштуйте змінні:
```bash
cp env.example .env
```

5. Запустіть через Docker:
```bash
docker-compose up -d
```

## Використання

### API Endpoints

- `GET /` - інформація про API
- `GET /health` - перевірка здоров'я
- `POST /api/v1/payments/validate` - валідація клієнта
- `POST /api/v1/payments/create` - створення платежу
- `GET /api/v1/payments/{id}/status` - статус платежу
- `POST /api/v1/payments/{id}/confirm` - підтвердження платежу

### Веб-хуки

- `POST /api/v1/webhooks/monobank/callback` - callback від Monobank
- `POST /api/v1/webhooks/bitrix/callback` - callback від Bitrix24

## Тестування

```bash
# Запуск тестів
pytest

# З покриттям
pytest --cov=app
```

## Розробка

```bash
# Форматування коду
black app/
isort app/

# Перевірка стилю
flake8 app/
mypy app/
```

## Деплой

1. Налаштуйте змінні середовища
2. Запустіть міграції БД
3. Запустіть додаток:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## SOLID принципи

- **Single Responsibility** - кожен клас має одну відповідальність
- **Open/Closed** - відкритий для розширення, закритий для модифікації
- **Liskov Substitution** - похідні класи можуть замінювати базові
- **Interface Segregation** - інтерфейси розділені за функціональністю
- **Dependency Inversion** - залежність від абстракцій

## Ліцензія

MIT
