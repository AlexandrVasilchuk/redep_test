# Телеграм Бот на основе Python
Этот проект представляет собой пример реализации телеграм-бота на Python с использованием фреймворка python-telegram-bot.

## Описание
Этот бот предназначен для управления приложениями и предоставления различной информации пользователям.


## Запуск бота
- Заполните .env file по образцу

```.env
#Переменная необходимая для подключения alembic к БД. Используется FastApi контейнером
BOT_TOKEN=****:******
DB_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
SECRET_ADMIN_TOKEN=SECRET_ADMIN_TOKEN
```

Запустите docker-compose.yml файл
```bash
docker-compose up -d --build  
```
Чтобы получить доступ к пользователю с ролью администратор - введите /start SECRET_ADMIN_TOKEN


---

## Использование
Этот бот имеет несколько команд:
### Команды для всех пользователей
/start <token> - регистрирует пользователя.  
/status - Выводит текущий статус всех приложений.  
/getlauchlinks - Выводит список приложений с возможностью получения ссылок для запуска.  
/faq - Отвечает на часто задаваемые вопросы.  

### Команды для администратора
/generatekey <token> - Генерирует новый ключ.  
/add <url> <name> <ads_url> - Добавляет новое приложение.  
/remove <url> - Удаляет существующее приложение.  
/broadcast <message> - Отправляет сообщение всем пользователям.  

## Взаимодействие с базой данных
Для работы с базой данных используется SQLAlchemy. Миграции базы данных выполняются с помощью alembic.