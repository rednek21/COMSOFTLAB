# COMSOFTLAB

## Конфигурация
Для запуска необходимо создать .env файл на внешнем уровне проекта(рядом с docker-compose) и заполнить по следующему примеру:

```
DEBUG=False
SECRET_KEY=
DOMAIN_NAME=http://0.0.0.0

DJANGO_SUPERUSER_PASSWORD=admin
DJANGO_SUPERUSER_EMAIL=admin@gmail.com
DJANGO_SUPERUSER_USERNAME=admin

DB=postgres
POSTGRES_NAME=comsoft_db
POSTGRES_USER=comsoft_user
POSTGRES_PASSWORD=
POSTGRES_DB=postgres
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

## Запуск и остановка 
Все просто:
```
docker compose up --build
```
```
docker compose down -v
```
