from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse, OpenApiExample

from blog.models import Like, Post
from blog.serializers import LikeSerializer
from blog.permissions import IsAuthorOrReadOnly


@extend_schema_view(
    create_like=extend_schema(
        summary="Поставить лайк посту",
        description="Поставляет лайк посту от имени авторизованного пользователя",
        tags=['Likes'],
        request=None,
        parameters=[
            OpenApiParameter(
                name='post_pk',
                description='ID поста',
                type=int,
                location=OpenApiParameter.PATH
            ),
        ],
        responses={
            201: OpenApiResponse(
                description='Лайк успешно поставлен',
                examples=[
                    OpenApiExample(
                        'Успешное создание',
                        value={"detail": "Пользователь john_doe лайкнул пост Привет, мир!"}
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Лайк уже поставлен',
                examples=[
                    OpenApiExample(
                        'Лайк уже существует',
                        value={"detail": "Лайк уже поставлен"}
                    )
                ]
            ),
            403: OpenApiResponse(description='Требуется авторизация'),
            404: OpenApiResponse(description='Пост не найден'),
        }
    ),
    delete_like=extend_schema(
        summary="Удалить лайк с поста",
        description="Удаляет лайк с поста от имени авторизованного пользователя",
        tags=['Likes'],
        request=None,
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
                description='Лайк успешно удален',
                examples=[
                    OpenApiExample(
                        'Успешное удаление',
                        value={"detail": "Лайк удален с поста Привет, мир!"}
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Лайк не найден',
                examples=[
                    OpenApiExample(
                        'Лайк не найден',
                        value={"detail": "Лайк не найден"}
                    )
                ],

            ),
            403: OpenApiResponse(description='Требуется авторизация'),
        }
    ),
)
class LikeViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = LikeSerializer

    @action(detail=False, methods=['post'], url_path='(?P<post_pk>[^/.]+)/create')
    def create_like(self, request, post_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Пост не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        like, created = Like.objects.get_or_create(post=post, user=user)

        if created:
            return Response(
                {'detail': f'Пользователь {user.username} лайкнул пост {post.title}'},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {'detail': 'Лайк уже поставлен'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['delete'], url_path='(?P<post_pk>[^/.]+)/delete')
    def delete_like(self, request, post_pk=None):
        try:
            post = Post.objects.get(id=post_pk)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Пост не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            return Response(
                {'detail': f'Лайк удален с поста {post.title}'},
                status=status.HTTP_200_OK
            )
        except Like.DoesNotExist:
            return Response(
                {'detail': 'Лайк не найден'},
                status=status.HTTP_404_NOT_FOUND
            )