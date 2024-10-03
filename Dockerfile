FROM python:3.12.3

WORKDIR /app

COPY . .

RUN  pip install -r requirements.txt
RUN docker network create MGNetwork

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]