from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample

from blog.models import Comment, Post
from blog.serializers import CommentSerializer
from blog.permissions import IsAuthorOrReadOnly


@extend_schema_view(
    create_comment=extend_schema(
        summary="Создать комментарий к посту",
        description="Создаёт новый комментарий к посту с указанным post_pk",
        tags=['Comments'],
        parameters=[
            OpenApiParameter(
                name='post_pk',
                description='ID поста',
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        request=CommentSerializer,
        responses={
            201: OpenApiResponse(
                description='Комментарий успешно создан',
                response=CommentSerializer,
                examples=[
                    OpenApiExample(
                        'Успешное создание',
                        value={
                            "id": 1,
                            "post": "Привет, мир!",
                            "author": "john_doe",
                            "content": "Отличный пост!",
                            "created_at": "2024-01-15T11:00:00Z"
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
    delete_comment=extend_schema(
        summary="Удалить комментарий",
        description="Удаляет комментарий по ID (только автор)",
        request=None,
        tags=['Comments'],
        parameters=[
            OpenApiParameter(
                name='post_pk',
                description='ID поста (передается в пути)',
                type=int,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='comment_pk',
                description='ID комментария (передается в пути)',
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Комментарий успешно удален',
                examples=[
                    OpenApiExample(
                        'Успешное удаление',
                        value={"detail": "Комментарий к посту \"Привет, мир!\" был удален"}
                    )
                ]
            ),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Комментарий не найден'),
        }
    ),
    update_comment=extend_schema(
        summary="Обновить комментарий",
        description="Обновляет содержимое комментария (только автор)",
        tags=['Comments'],
        parameters=[
            OpenApiParameter(
                name='post_pk',
                description='ID поста (передается в пути)',
                type=int,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='comment_pk',
                description='ID комментария (передается в пути)',
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        request=CommentSerializer,
        responses={
            200: OpenApiResponse(
                description='Комментарий успешно обновлен',
                response=CommentSerializer,
                examples=[
                    OpenApiExample(
                        'Успешное обновление',
                        value={
                            "id": 1,
                            "post": "Привет, мир!",
                            "author": "john_doe",
                            "content": "Обновленное содержание",
                            "created_at": "2024-01-15T11:00:00Z"
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Недостаточно прав'),
            404: OpenApiResponse(description='Комментарий не найден'),
        }
    ),
    get_comments=extend_schema(
        summary="Получить список комментариев к посту",
        description="Возвращает все комментарии к посту с указанным post_pk",
        tags=['Comments'],
        parameters=[
            OpenApiParameter(
                name='post_pk',
                description='ID поста',
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Список комментариев',
                response=CommentSerializer,
                examples=[
                    OpenApiExample(
                        'Успешный ответ',
                        value=[
                            {
                                "id": 1,
                                "post": "Привет, мир!",
                                "author": "john_doe",
                                "content": "Отличный пост!",
                                "created_at": "2024-01-15T11:00:00Z"
                            },
                            {
                                "id": 2,
                                "post": "Привет, мир!",
                                "author": "jane_smith",
                                "content": "Спасибо за информацию!",
                                "created_at": "2024-01-15T12:00:00Z"
                            }
                        ]
                    )
                ]
            ),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
)
class CommentViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthorOrReadOnly,IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    @action(detail=False, methods=['post'], url_path='(?P<post_pk>[^/.]+)/create')
    def create_comment(self, request, post_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Пост не найден'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        content = request.data.get('content')
        if not content:
            return Response({'detail': 'Пустое содержание комментария'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(post=post, author=user, content=content)

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='(?P<post_pk>[^/.]+)/delete/(?P<comment_pk>[^/.]+)')
    def delete_comment(self, request, post_pk=None, comment_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Пост не найден'}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = Comment.objects.get(id=comment_pk)
        except Comment.DoesNotExist:
            return Response({'detail': 'Комментарий не найден'}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, comment)

        post_title = post.title
        comment.delete()

        return Response(
            {'detail': f'Комментарий к посту "{post_title}" был удален'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['patch'], url_path='(?P<post_pk>[^/.]+)/update/(?P<comment_pk>[^/.]+)')
    def update_comment(self, request, post_pk=None, comment_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Пост не найден'}, status=status.HTTP_404_NOT_FOUND)

        try:
            comment = Comment.objects.get(id=comment_pk, post=post)
        except Comment.DoesNotExist:
            return Response({'detail': 'Комментарий не найден'}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, comment)

        comment.content = request.data.get('content')

        if not comment.content:
            return Response({'detail': 'Пустое содержание комментария'}, status=status.HTTP_400_BAD_REQUEST)

        comment.save()
        serializer = CommentSerializer(comment)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='(?P<post_pk>[^/.]+)/list')
    def get_comments(self, request, post_pk=None):
        post = get_object_or_404(Post, id=post_pk)

        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



    # def destroy(self, request, *args, **kwargs):
    #     comment = self.get_object()
    #     post_title = comment.post.title
    #
    #     super().destroy(request, *args, **kwargs)
    #
    #     return Response(
    #         {'detail': f'Комментарий к посту "{post_title}" был удален'},
    #         status=status.HTTP_200_OK
    #     )