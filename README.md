# Документация по запуску проекта

## Описание

Данный проект представляет собой веб-приложение, использующее Django и PostgreSQL в качестве базы данных. Приложение упаковано в контейнеры с помощью Docker и управляется с помощью Docker Compose.

---

## Требования

Перед началом убедитесь, что у вас установлены следующие инструменты:

- [Docker](https://docs.docker.com/get-docker/) (версия 20.10 или выше)
- [Docker Compose](https://docs.docker.com/compose/install/) (версия 1.27 или выше)

---

## Установка

### 1. Клонируйте репозиторий

Выполните команду для клонирования репозитория:

```bash
git clone https://github.com/colrosezx/manager_passwords.git
cd manager_passwords
```

### 2. Создайте файл .env
В корневой директории проекта создайте файл .env и добавьте в него переменные окружения из .env-example.
Сгенерируйте SERCET_KEY:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Соберите и запустите контейнеры. В корневой директории проекта выполните команду:

```bash
docker-compose up --build
```

### 3. Проверьте, что контейнеры запущены

```bash
docker ps
```

### 4. Доступ к приложению
Откройте браузер и перейдите по адресу:
http://localhost:8000
