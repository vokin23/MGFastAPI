Определить папку миграций - alembic init app/migrations
Сгенерировать миграцию - alembic revision --autogenerate
Применить миграцию - alembic upgrade head

Расширить файл requirements.txt новой зависимостью - pip freeze > requirements.txt

Запуск проекта из папки app - uvicorn app.main:app --reload
