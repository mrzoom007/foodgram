---

**Foodgram — кулинарный помощник с базой рецептов**

Foodgram — это приложение для любителей кулинарии, которое позволяет публиковать свои рецепты, сохранять понравившиеся и автоматически генерировать список покупок для выбранных блюд. Пользователи могут подписываться на авторов, которые им интересны, и следить за новыми публикациями.

**Основные возможности проекта**:

- Публикация, сохранение и организация рецептов
- Формирование списка покупок на основе выбранных рецептов
- Подписка на авторов рецептов
- Простота в использовании и интуитивно понятный интерфейс

**API и документация**:

Проект предоставляет удобное API для работы с данными и интеграции с внешними системами. Документация к API доступна по [ссылке](#), где описаны доступные запросы и структура ответов. Для каждого запроса указаны уровни прав доступа, что позволяет гибко управлять доступом.

**Технологии, использованные в проекте**:

- Python, Django, Django Rest Framework
- Docker, Gunicorn, NGINX
- PostgreSQL, Yandex Cloud
- CI/CD (Continuous Integration, Continuous Deployment)

**Шаги по развертыванию проекта на удаленном сервере**:

1. **Клонировать репозиторий**:
   ```bash
   git clone git@github.com:mrzoom007/foodgram.git
   ```

2. **Установить Docker и Docker Compose** на сервер:
   ```bash
   sudo apt install curl
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo apt-get install docker-compose-plugin
   ```

3. **Копировать файлы конфигурации** (docker-compose.yml и nginx.conf) на сервер:
   ```bash
   scp docker-compose.yml nginx.conf username@IP:/home/username/
   ```

4. **Настроить переменные окружения на GitHub Actions**:
   Создать переменные окружения в разделе **Secrets** репозитория:
   - `SECRET_KEY`, `DOCKER_PASSWORD`, `DOCKER_USERNAME`
   - `HOST`, `USER`, `PASSPHRASE`, `SSH_KEY`
   - Настроить подключение к базе данных PostgreSQL и прочие переменные.

5. **Запустить проект на сервере**:
   После копирования файлов, на сервере выполняем команду для запуска контейнеров:
   ```bash
   sudo docker compose up -d
   ```

6. **Выполнить миграции базы данных**:
   ```bash
   sudo docker compose exec backend python manage.py migrate
   ```

7. **Создать суперпользователя**:
   ```bash
   sudo docker compose exec backend python manage.py createsuperuser
   ```

8. **Собрать статику**:
   ```bash
   sudo docker compose exec backend python manage.py collectstatic --noinput
   ```

9. **Заполнить базу данных**:
   ```bash
   sudo docker compose exec backend python manage.py loaddata ingredients.json
   ```

10. **Для остановки контейнеров**:
    ```bash
    sudo docker compose down -v
    sudo docker compose stop
    ```


11. ДАННЫЕ ДЛЯ АДМИНКИ: 
```
Логин - Admin 
Пароль - Admin
Email - Adminadmin@admin.com
```

12. РАСПОЛОЖЕНИЕ: 
```
Проект будет доступен по адресу 
https://igorfoodgram.zapto.org/signin
```