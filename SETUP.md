# Інструкції по запуску SmartKasa Integration

## Швидкий старт

### 1. Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 2. Налаштування змінних середовища
```bash
cp env.example .env
# Відредагуйте .env файл з вашими налаштуваннями
```

### 3. Запуск через Docker (рекомендовано)
```bash
docker-compose up -d
```

### 4. Або запуск локально
```bash
python run.py
```

## Доступ до API

- **API документація**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## Основні endpoints

### Платежі
- `POST /api/v1/payments/validate` - валідація клієнта
- `POST /api/v1/payments/create` - створення платежу
- `GET /api/v1/payments/{id}/status` - статус платежу
- `POST /api/v1/payments/{id}/confirm` - підтвердження платежу

### Клієнти
- `POST /api/v1/customers/` - створення клієнта
- `GET /api/v1/customers/{id}` - отримання клієнта
- `PUT /api/v1/customers/{id}` - оновлення клієнта

### Веб-хуки
- `POST /api/v1/webhooks/monobank/callback` - callback від Monobank
- `POST /api/v1/webhooks/bitrix/callback` - callback від Bitrix24

## Тестування

```bash
# Запуск тестів API
python scripts/test_api.py

# Ініціалізація БД
python scripts/init_db.py
```

## Архітектура

Проект побудований згідно з принципами SOLID:

- **Single Responsibility** - кожен клас має одну відповідальність
- **Open/Closed** - відкритий для розширення, закритий для модифікації  
- **Liskov Substitution** - похідні класи можуть замінювати базові
- **Interface Segregation** - інтерфейси розділені за функціональністю
- **Dependency Inversion** - залежність від абстракцій

## Структура

```
app/
├── core/interfaces/     # Абстракції
├── models/             # Моделі БД
├── schemas/            # Pydantic схеми
├── services/           # Бізнес-логіка
├── repositories/       # Доступ до даних
├── api/v1/            # API endpoints
├── webhooks/          # Обробка веб-хуків
└── utils/             # Утиліти
```

## Моніторинг

- Логи доступні в консолі або через Docker logs
- Health check endpoint для перевірки стану
- Автоматична документація API

## Безпека

- HMAC-SHA256 підписи для веб-хуків
- Валідація всіх вхідних даних через Pydantic
- CORS налаштування
- Захищені змінні середовища
