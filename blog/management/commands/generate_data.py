import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Post, Comment, Like

UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Генерирует тестовые данные: пользователей, посты, комментарии и лайки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Количество пользователей для создания (по умолчанию: 10)'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=50,
            help='Количество постов для создания (по умолчанию: 50)'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=150,
            help='Количество комментариев для создания (по умолчанию: 150)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все существующие данные перед генерацией'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_posts = options['posts']
        num_comments = options['comments']
        should_clear = options['clear']

        if should_clear:
            self.stdout.write(self.style.WARNING('Очистка существующих данных...'))
            Like.objects.all().delete()
            Comment.objects.all().delete()
            Post.objects.all().delete()
            # Не удаляем суперпользователей
            regular_users = UserModel.objects.filter(is_superuser=False)
            regular_users.delete()
            self.stdout.write(self.style.SUCCESS('Данные очищены'))

        # Создание пользователей
        self.stdout.write('Создание пользователей...')
        users = []
        
        # Создаем суперпользователя
        if not UserModel.objects.filter(username='admin').exists():
            admin = UserModel.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                bio='Администратор системы'
            )
            users.append(admin)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан суперпользователь: {admin.username}'))

        # Создаем обычных пользователей
        first_names = ['Алексей', 'Мария', 'Дмитрий', 'Елена', 'Иван', 'Ольга', 
                      'Сергей', 'Анна', 'Максим', 'Наталья', 'Александр', 'Екатерина',
                      'Павел', 'Татьяна', 'Андрей', 'Юлия', 'Михаил', 'Виктория']
        last_names = ['Иванов', 'Петрова', 'Сидоров', 'Смирнова', 'Кузнецов', 'Попов',
                     'Васильев', 'Соколова', 'Михайлов', 'Новикова', 'Федоров', 'Морозова',
                     'Волков', 'Лебедева', 'Козлов', 'Николаев', 'Орлов', 'Захарова']
        
        usernames = ['alex', 'maria', 'dmitry', 'elena', 'ivan', 'olga',
                    'sergey', 'anna', 'maxim', 'natasha', 'alexander', 'ekaterina',
                    'pavel', 'tatyana', 'andrey', 'yulia', 'mikhail', 'victoria']
        
        for i in range(min(num_users, len(usernames))):
            username = usernames[i]
            if UserModel.objects.filter(username=username).exists():
                continue
                
            user = UserModel.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='password123',
                first_name=first_names[i % len(first_names)],
                last_name=last_names[i % len(last_names)],
                bio=f'Биография пользователя {username}. Люблю технологии и программирование.',
                github_username=f'{username}_gh'
            )
            users.append(user)
            self.stdout.write(f'  ✓ Создан пользователь: {user.username}')

        # Создание постов
        self.stdout.write('\nСоздание постов...')
        titles = [
            'Как начать программировать на Python',
            'Топ 10 фреймворков для веб-разработки',
            'Мой опыт работы с Django',
            'React vs Vue: сравнение',
            'Основы алгоритмов и структур данных',
            'Git для начинающих',
            'Как стать DevOps инженером',
            'Тренды программирования 2024',
            'Создание REST API',
            'Работа с базами данных',
            'Микросервисы против монолита',
            'Тестирование в Python',
            'Docker для начинающих',
            'Кubernetes: полное руководство',
            'CI/CD пайплайны',
            'Автоматизация с помощью Python',
            'Работа с API: лучшие практики',
            'Безопасность веб-приложений',
            'Оптимизация производительности',
            'Архитектура программного обеспечения'
        ]
        
        contents = [
            'Это подробное руководство по теме, которое поможет вам разобраться во всех нюансах. Мы рассмотрим основные концепции, приведем примеры кода и дадим практические советы.',
            'В этой статье я делюсь своим опытом и знаниями. Надеюсь, это будет полезно как начинающим, так и опытным разработчикам.',
            'Сегодня поговорим о важной теме в мире программирования. Это одна из тех вещей, которые должен знать каждый разработчик.',
            'Давайте разберем этот вопрос подробно. Я собрал лучшие материалы и примеры, которые помогут вам в изучении.',
            'Эта тема вызывает много споров в сообществе. Я постараюсь быть объективным и показать разные точки зрения.',
            'Вот мое видение ситуации. Не стесняйтесь делиться своими мыслями в комментариях!',
            'Это руководство основано на моем многолетнем опыте работы в индустрии.',
            'Современная разработка требует знания этих инструментов. Вот почему они так важны.',
            'Я потратил много времени на изучение этой темы и готов поделиться результатами.',
            'Практические примеры помогут лучше понять материал. Попробуйте повторить их самостоятельно.'
        ]
        
        posts = []
        for i in range(num_posts):
            title = titles[i % len(titles)]
            if num_posts > len(titles):
                title = f'{title} ({i // len(titles) + 1})'
            
            post = Post.objects.create(
                title=title,
                content=random.choice(contents) + '\n\n' + random.choice(contents),
                author=random.choice(users)
            )
            posts.append(post)
            
            # Добавляем дату создания в прошлом
            random_days_ago = random.randint(0, 365)
            post.created_at = datetime.now() - timedelta(days=random_days_ago)
            post.updated_at = post.created_at + timedelta(hours=random.randint(1, 48))
            post.save()
            
            if (i + 1) % 10 == 0 or i == num_posts - 1:
                self.stdout.write(f'  ✓ Создано постов: {i + 1}/{num_posts}')

        # Создание комментариев
        self.stdout.write('\nСоздание комментариев...')
        comment_texts = [
            'Отличная статья! Спасибо за подробное объяснение.',
            'Интересная точка зрения, никогда об этом не думал.',
            'Можно ли привести пример кода?',
            'У меня возник вопрос по этой теме. Не могли бы вы уточнить?',
            'Я тоже сталкивался с этой проблемой. Решение действительно работает.',
            'Спасибо за полезную информацию!',
            'Очень полезно, особенно для начинающих.',
            'Не согласен с этим утверждением. Вот почему...',
            'А как насчет альтернативного подхода?',
            'Отличная работа! Продолжайте в том же духе.',
            'Мне понравилось, как вы это объяснили.',
            'Есть ли какие-то книги по этой теме?',
            'Это помогло мне решить мою проблему. Спасибо!',
            'Интересно, а как это работает в продакшене?',
            'Замечательное руководство! Добавил в закладки.',
            'Возникла ошибка при выполнении примера. Кто-нибудь сталкивался?',
            'Как вы думаете, это актуально в 2024 году?',
            'Отлично структурирован материал!',
            'Могу ли я использовать этот код в своем проекте?',
            'Спасибо за время, уделенное этой статье!'
        ]
        
        comments_created = 0
        for i in range(num_comments):
            post = random.choice(posts)
            # Не все комментарии от разных пользователей (некоторые пользователи пишут больше)
            author = random.choice(users)
            
            comment = Comment.objects.create(
                post=post,
                author=author,
                content=random.choice(comment_texts)
            )
            comments_created += 1
            
            # Случайная дата создания
            random_hours_ago = random.randint(0, 8760)  # до года назад
            comment.created_at = datetime.now() - timedelta(hours=random_hours_ago)
            comment.save()
            
            if (i + 1) % 25 == 0 or i == num_comments - 1:
                self.stdout.write(f'  ✓ Создано комментариев: {i + 1}/{num_comments}')

        # Создание лайков
        self.stdout.write('\nСоздание лайков...')
        likes_created = 0
        
        # Для каждого поста создаем случайное количество лайков
        for post in posts:
            # Случайное количество лайков от 0 до 20
            num_likes_for_post = random.randint(0, min(20, len(users)))
            
            # Выбираем случайных пользователей для лайка
            likers = random.sample(users, min(num_likes_for_post, len(users)))
            
            for user in likers:
                # Проверяем, нет ли уже лайка
                if not Like.objects.filter(post=post, user=user).exists():
                    Like.objects.create(post=post, user=user)
                    likes_created += 1

        self.stdout.write(f'  ✓ Создано лайков: {likes_created}')

        # Статистика
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Генерация данных завершена!'))
        self.stdout.write('='*50)
        self.stdout.write(f'Пользователей: {UserModel.objects.count()}')
        self.stdout.write(f'Постов: {Post.objects.count()}')
        self.stdout.write(f'Комментариев: {Comment.objects.count()}')
        self.stdout.write(f'Лайков: {Like.objects.count()}')
        self.stdout.write('='*50)
        
        # Выводим информацию для входа
        self.stdout.write(self.style.WARNING('\nТестовые учетные данные:'))
        self.stdout.write('  Суперпользователь: admin / admin123')
        self.stdout.write('  Обычные пользователи: username / password123')
        self.stdout.write('  Примеры: alex, maria, dmitry, elena, ivan...')