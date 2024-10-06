Определить папку миграций - alembic init app/migrations
Сгенерировать миграцию - alembic revision --autogenerate
Применить миграцию - alembic upgrade head

Расширить файл requirements.txt новой зависимостью - pip freeze > requirements.txt

Запуск проекта из папки app - uvicorn app.main:app --reload


docker network create test

docker run --name test_db -p 5436:5433 -e POSTGRES_HOST=test_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=test --network=test -d postgres:16

docker run --name redis_test -p 7379:6379 --network=test -d redis:7.4

docker run --name booking_back -p 7777:8000  --network=test booking_image
