# 📚 Инструкция по загрузке проекта на GitHub

## 🚀 Быстрый старт

Ваш проект уже подготовлен для загрузки на GitHub! Выполните следующие шаги:

### 1. Создание репозитория на GitHub

1. Перейдите на [GitHub.com](https://github.com)
2. Нажмите кнопку **"New"** или **"+"** → **"New repository"**
3. Заполните данные:
   - **Repository name**: `telegram-bots-collection` (или любое другое название)
   - **Description**: `Collection of Telegram bots for investments, real estate, and insurance with web interface`
   - **Visibility**: `Public` или `Private` (на ваш выбор)
   - ❌ **НЕ** ставьте галочки на "Add a README file", "Add .gitignore", "Choose a license"
4. Нажмите **"Create repository"**

### 2. Подключение локального репозитория к GitHub

Выполните команды в терминале (в папке проекта):

```bash
# Добавить удаленный репозиторий (замените YOUR_USERNAME и YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Переименовать главную ветку в main (современный стандарт)
git branch -M main

# Загрузить код на GitHub
git push -u origin main
```

### 3. Настройка переменных окружения

⚠️ **ВАЖНО**: Файл `.env` содержит только примеры токенов и безопасен для публикации.

Для работы с ботами:
1. Скопируйте `.env` в `.env.local`
2. Заполните `.env.local` реальными токенами
3. Используйте `.env.local` для локальной разработки

## 🔧 Дополнительные настройки

### Настройка Git (если не настроен)

```bash
# Настройка имени и email (выполните один раз)
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"
```

### Клонирование репозитория на другом компьютере

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Создать .env.local с реальными токенами
cp .env .env.local
# Отредактируйте .env.local

# Установить зависимости
pip install -r requirements.txt
```

## 📋 Структура проекта на GitHub

```
telegram-bots-collection/
├── 🤖 bots/                    # Telegram боты
│   ├── BOT_Inv.py             # Инвестиционный бот
│   ├── BOT_Ocenka.py          # Бот оценки
│   ├── BOT_P.py               # Бот недвижимости
│   ├── BOT_PR.py              # Бот PR
│   └── BOT_Str.py             # Страховой бот
├── 🌐 web/                     # Веб-интерфейс
│   ├── assets/qr/             # QR-коды
│   └── index.html             # Главная страница
├── 🏠 perm_realty_bot_v2/      # Продвинутый бот недвижимости
├── 📚 docs/                    # Документация
├── 🚀 railway.json             # Конфигурация Railway
├── 🐳 Dockerfile               # Docker конфигурация
├── 📋 requirements.txt         # Python зависимости
├── 🔒 .env                     # Примеры переменных (безопасно)
├── 🚫 .gitignore              # Исключения Git
└── 📖 README.md               # Документация проекта
```

## 🔐 Безопасность

### Что НЕ попадет в репозиторий (благодаря .gitignore):
- ✅ `.env.local` - ваши реальные токены
- ✅ `*.log` - лог файлы
- ✅ `__pycache__/` - кэш Python
- ✅ `venv/` - виртуальное окружение

### Что безопасно загружать:
- ✅ `.env` - содержит только примеры
- ✅ `.env.example` - шаблон для настройки
- ✅ Весь код ботов
- ✅ Документация
- ✅ Конфигурационные файлы

## 🚀 Развертывание

После загрузки на GitHub вы можете:

1. **Railway**: Используйте `RAILWAY_DEPLOYMENT.md`
2. **Docker**: Используйте `Dockerfile` и `docker-compose.yml`
3. **Heroku**: Добавьте `Procfile` при необходимости
4. **VPS**: Клонируйте репозиторий и запустите

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте, что все команды выполнены в правильной папке
2. Убедитесь, что Git настроен (имя и email)
3. Проверьте права доступа к репозиторию на GitHub
4. При ошибках аутентификации используйте Personal Access Token вместо пароля

---

✅ **Проект готов к публикации на GitHub!**