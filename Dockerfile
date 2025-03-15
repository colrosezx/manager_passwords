FROM python:latest

WORKDIR /app

COPY . /app/

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt


CMD bash -c " \
    echo 'Запуск API service...'; \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000"