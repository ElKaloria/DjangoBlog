# Blog API

REST API для блога на Django с возможностью создания постов, комментариев, лайков и аутентификации пользователей.

## 📋 Описание

Проект представляет собой REST API для блога на Django, включающий:

- **Аутентификацию пользователей**: регистрация, вход, выход, профиль
- **Посты**: создание, чтение, обновление, удаление (CRUD)
- **Комментарии**: добавление и управление комментариями к постам
- **Лайки**: система лайков для постов
- **Фильтрацию и сортировку**: гибкие возможности работы с данными
- **Swagger документацию**: интерактивная документация API
- **Комплексные тесты**: покрытие всех API endpoints
- **Генератор тестовых данных**: быстрый старт с тестовыми данными


## 🛠️ Технологический стек
### Backend
- **Django** — веб-фреймворк
- **Django REST Framework** — создание API
- **PostgreSQL** — база данных
- **django-filter** — фильтрация запросов
- **drf-spectacular** — генерация OpenAPI документации

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Git

### Запуск проекта

1. **Клонируйте репозиторий**
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```

2. **Настройте переменные окружения**
   ```bash
   cp backend/env_sample backend/.env
   cp backend/postgres.env_sample backend/postgres.env
   ```

   Отредактируйте `.env` и добавьте свои значения:

    ```env
    SECRET_KEY=your-secret-key-here
    DEBUG=True
    
    SOCIAL_AUTH_GITHUB_KEY=your-github-key - Для oauth github авторизации
    SOCIAL_AUTH_GITHUB_SECRET=your-github-secret
    ```

   Для создания GitHub app воспользуйтесь руководством по ссылке
   https://docs.github.com/ru/apps/creating-github-apps/about-creating-github-apps/about-creating-github-apps

4. **Запустите проект**
   ```bash
   docker-compose up -d --build
   ```
   
5. **Создайте суперпользователя**
   ```bash
   python manage.py createsuperuser
   ```

6. **Добавьте демо-данные** (опционально)
   ```bash
   python manage.py generate_data
   ```

## 🔌 API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register/` | Регистрация пользователя |
| POST | `/api/auth/login/` | Вход в систему |
| POST | `api/auth/login/github/` | Вход в систему через GitHub |
| POST | `/api/auth/logout/` | Выход из системы |
| GET/PATCH/PUT | `/api/auth/profile/` | Управление профилем |

### Посты

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/posts/` | Получить список постов |
| POST | `/api/posts/` | Создать пост |
| GET | `/api/posts/{id}/` | Получить пост |
| PUT | `/api/posts/{id}/` | Обновить пост |
| PATCH | `/api/posts/{id}/` | Частично обновить пост |
| DELETE | `/api/posts/{id}/` | Удалить пост |

**Параметры фильтрации:**
- `author` - фильтр по username автора
- `created_at` - фильтр по дате создания
- `ordering` - сортировка (created_at, author, likes_count, comments_count)

### Комментарии

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/comments/{post_pk}/create` | Создать комментарий |
| GET | `/api/comments/{post_pk}/list` | Получить комментарии поста |
| PATCH | `/api/comments/{comment_pk}/update` | Обновить комментарий |
| DELETE | `/api/comments/{comment_pk}/delete` | Удалить комментарий |

### Лайки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/likes/{post_pk}/create` | Поставить лайк |
| DELETE | `/api/likes/{post_pk}/delete` | Удалить лайк |

## 📖 Документация API

### Swagger UI

Интерактивная документация с возможностью тестирования endpoints:

```
http://localhost:8000/api/docs/swagger/
```

### ReDoc

Альтернативная документация в формате ReDoc:

```
http://localhost:8000/api/docs/redoc/
```

### OpenAPI Schema

JSON схема API:

```
http://localhost:8000/api/schema/
```

### Тестирование

```bash
# Backend тесты
python manage.py test
