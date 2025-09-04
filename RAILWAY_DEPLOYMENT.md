# Развертывание проекта на Railway

## Обзор проекта

Проект содержит 6 Telegram ботов:
- **BOT_Inv.py** - Инвестиционный бот
- **BOT_Ocenka.py** - Бот оценки недвижимости
- **BOT_P.py** - Бот заявок на покупку
- **BOT_PR.py** - Бот заявок на продажу
- **BOT_Str.py** - Страховой бот
- **perm_realty_bot_v2** - Бот недвижимости Перми (v2)

## Структура проекта

```
├── bots/                    # Основные боты
│   ├── BOT_Inv.py
│   ├── BOT_Ocenka.py
│   ├── BOT_P.py
│   ├── BOT_PR.py
│   └── BOT_Str.py
├── perm_realty_bot_v2/      # Бот недвижимости v2
├── web/                     # Веб-интерфейс
│   ├── index.html
│   └── assets/
├── docs/                    # Документация
├── .github/workflows/       # GitHub Actions
├── requirements.txt         # Зависимости Python
├── Dockerfile              # Docker конфигурация
├── docker-compose.yml      # Docker Compose
├── railway.json            # Конфигурация Railway
└── .env.example            # Пример переменных окружения
```

## Подготовка к развертыванию

### 1. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example` и заполните:

```env
# Токены ботов (получить у @BotFather)
BOT_TOKEN_INV=your_investment_bot_token
BOT_TOKEN_OCENKA=your_appraisal_bot_token
BOT_TOKEN_P=your_purchase_bot_token
BOT_TOKEN_PR=your_sales_bot_token
BOT_TOKEN_STR=your_insurance_bot_token
BOT_TOKEN=your_realty_bot_v2_token

# ID администратора (получить у @userinfobot)
ADMIN_CHAT_ID=your_admin_chat_id
```

### 2. Проверка зависимостей

Убедитесь, что `requirements.txt` содержит все необходимые пакеты:

```txt
pyTelegramBotAPI==4.14.0
requests==2.31.0
aiogram==3.4.1
aiosqlite==0.19.0
```

## Развертывание на Railway

### Вариант 1: Через GitHub (Рекомендуется)

1. **Загрузите код в GitHub репозиторий**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **Подключите Railway к GitHub**
   - Зайдите на [railway.app](https://railway.app)
   - Войдите через GitHub
   - Нажмите "New Project" → "Deploy from GitHub repo"
   - Выберите ваш репозиторий

3. **Настройте переменные окружения в Railway**
   - В панели Railway перейдите в "Variables"
   - Добавьте все переменные из `.env` файла
   - **Важно**: Не загружайте `.env` файл в репозиторий!

### Вариант 2: Через Railway CLI

1. **Установите Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Войдите в Railway**
   ```bash
   railway login
   ```

3. **Инициализируйте проект**
   ```bash
   railway init
   ```

4. **Разверните проект**
   ```bash
   railway up
   ```

## Настройка отдельных сервисов

### Для каждого бота создайте отдельный сервис:

1. **Investment Bot (BOT_Inv.py)**
   - Start Command: `python bots/BOT_Inv.py`
   - Environment: `BOT_TOKEN_INV`, `ADMIN_CHAT_ID`

2. **Appraisal Bot (BOT_Ocenka.py)**
   - Start Command: `python bots/BOT_Ocenka.py`
   - Environment: `BOT_TOKEN_OCENKA`, `ADMIN_CHAT_ID`

3. **Purchase Bot (BOT_P.py)**
   - Start Command: `python bots/BOT_P.py`
   - Environment: `BOT_TOKEN_P`, `ADMIN_CHAT_ID`

4. **Sales Bot (BOT_PR.py)**
   - Start Command: `python bots/BOT_PR.py`
   - Environment: `BOT_TOKEN_PR`, `ADMIN_CHAT_ID`

5. **Insurance Bot (BOT_Str.py)**
   - Start Command: `python bots/BOT_Str.py`
   - Environment: `BOT_TOKEN_STR`, `ADMIN_CHAT_ID`

6. **Realty Bot v2**
   - Start Command: `python -m app.main`
   - Working Directory: `perm_realty_bot_v2`
   - Environment: `BOT_TOKEN`, `ADMIN_CHAT_ID`

## Мониторинг и логи

### Просмотр логов
```bash
railway logs
```

### Проверка статуса сервисов
```bash
railway status
```

### Перезапуск сервиса
```bash
railway restart
```

## Рекомендации по оптимизации

### 1. Использование Docker
Для стабильной работы рекомендуется использовать Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bots/BOT_Inv.py"]
```

### 2. Настройка автоматического развертывания
Настройте GitHub Actions для автоматического развертывания при push:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Use Railway
      uses: railway-app/railway@v1
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
      env:
        RAILWAY_PROJECT_ID: ${{ secrets.RAILWAY_PROJECT_ID }}
```

### 3. Мониторинг ресурсов
- Следите за использованием CPU и памяти
- Настройте алерты для критических ошибок
- Регулярно проверяйте логи ботов

## Устранение неполадок

### Частые проблемы:

1. **Бот не отвечает**
   - Проверьте правильность токена
   - Убедитесь, что бот запущен (@BotFather)
   - Проверьте логи на наличие ошибок

2. **Ошибки импорта**
   - Убедитесь, что все зависимости указаны в `requirements.txt`
   - Проверьте версии пакетов

3. **Проблемы с переменными окружения**
   - Убедитесь, что все переменные заданы в Railway
   - Проверьте правильность названий переменных

### Полезные команды:

```bash
# Проверка переменных окружения
railway variables

# Подключение к контейнеру
railway shell

# Просмотр метрик
railway metrics
```

## Поддержка

Для получения помощи:
1. Проверьте логи Railway
2. Обратитесь к документации Railway: https://docs.railway.app
3. Проверьте статус Telegram API: https://status.telegram.org

---

**Примечание**: Убедитесь, что у вас есть активная подписка Railway для развертывания нескольких сервисов одновременно.