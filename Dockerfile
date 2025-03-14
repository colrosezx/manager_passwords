# Используем официальный образ Python
FROM python:latest

# Устанавливаем зависимости для работы с приложением
WORKDIR /app

# Копируем все файлы из текущей директории в папку /app в контейнер
COPY . /app/
#COPY ./currency_timeframe_config.yaml /app/currency_timeframe_config.yaml
COPY ./requirements.txt requirements.txt

# Устанавливаем зависимости, указанные в requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


CMD bash -c " \
    echo 'Запуск API service...'; \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000"