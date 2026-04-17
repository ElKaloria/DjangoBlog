from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample

from blog.filters import PostFilter
from blog.models import Post
from blog.serializers import PostSerializer
from blog.permissions import IsAuthorOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="Получить список всех постов",
        description="Возвращает пагинированный список всех постов с возможностью фильтрации и сортировки",
        tags=['Posts'],
        request=None,
        parameters=[
            OpenApiParameter(
                name='author',
                description='Фильтр по username автора',
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='created_at',
                description='Фильтр по дате создания (YYYY-MM-DD)',
                type=str,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='ordering',
                description='Поле для сортировки',
                type=str,
                location=OpenApiParameter.QUERY,
                enum=['created_at', '-created_at', 'author', '-author', 'likes_count', '-likes_count', 'comments_count', '-comments_count']
            ),
            OpenApiParameter(
                name='page',
                description='Номер страницы пагинации',
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Успешный список постов',
                response=PostSerializer,
                examples=[
                    OpenApiExample(
                        'Успешный ответ',
                        value={
                            "count": 20,
                            "next": "http://localhost:8000/api/posts/?page=2",
                            "previous": None,
                            "results": [
                                {
                                    "id": 1,
                                    "title": "Привет, мир!",
                                    "content": "Это первый пост в блоге.",
                                    "author": "john_doe",
                                    "created_at": "2024-01-15T10:30:00Z",
                                    "updated_at": "2024-01-15T10:30:00Z",
                                    "amount_of_likes": 5,
                                    "amount_of_comments": 2
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Ошибка валидации данных')
        }
    ),
    create=extend_schema(
        summary="Создать новый пост",
        description="Создаёт новый пост от имени авторизованного пользователя",
        tags=['Posts'],
        request=PostSerializer,
        responses={
            201: OpenApiResponse(
                description='Пост успешно создан',
                response=PostSerializer,
                examples=[
                    OpenApiExample(
                        'Успешное создание',
                        value={
                            "id": 1,
                            "title": "Новый пост",
                            "content": "Содержимое поста",
                            "author": "john_doe",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z",
                            "amount_of_likes": 0,
                            "amount_of_comments": 0
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Ошибка валидации данных'),
            403: OpenApiResponse(description='Требуется авторизация')
        }
    ),
    retrieve=extend_schema(
        summary="Получить пост по ID",
        description="Возвращает детали поста по его уникальному идентификатору",
        tags=['Posts'],
        responses={
            200: OpenApiResponse(
                description='Детали поста',
                response=PostSerializer,
                examples=[
                    OpenApiExample(
                        'Успешный ответ',
                        value={
                            "id": 1,
                            "title": "Привет, мир!",
                            "content": "Это содержимое поста.",
                            "author": "john_doe",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z",
                            "amount_of_likes": 5,
                            "amount_of_comments": 2
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description='Пост не найден')
        }
    ),
    update=extend_schema(
        summary="Полностью обновить пост",
        description="Полностью обновляет пост (только автор)",
        tags=['Posts'],
        request=PostSerializer,
        responses={
            200: OpenApiResponse(description='Пост успешно обновлен'),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
    partial_update=extend_schema(
        summary="Частично обновить пост",
        description="Частично обновляет пост (только автор)",
        tags=['Posts'],
        request=PostSerializer,
        responses={
            200: OpenApiResponse(description='Пост успешно обновлен'),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
    destroy=extend_schema(
        summary="Удалить пост",
        description="Удаляет пост (только автор)",
        tags=['Posts'],
        responses={
            200: OpenApiResponse(
                description='Пост успешно удален',
                examples=[
                    OpenApiExample(
                        'Успешное удаление',
                        value={"detail": "Пост \"Привет, мир!\" был удален"}
                    )
                ]
            ),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True)
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PostFilter
    ordering_fields = [
        'created_at',
        'author',
        'likes_count',
        'comments_count'
    ]
    ordering = ['-created_at']


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        post_title = post.title

        super().destroy(request, *args, **kwargs)

        return Response(
            {'detail': f'Пост "{post_title}" был удален'},
            status=status.HTTP_200_OK
        )