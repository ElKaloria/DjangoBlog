from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample

from blog.serializers import UserSerializer, RegisterSerializer, LoginSerializer
from blog.models import CustomUser


@extend_schema_view(
    post=extend_schema(
        summary="Регистрация нового пользователя",
        description="Регистрирует нового пользователя с указанными учетными данными",
        tags=['Authentication'],
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description='Пользователь успешно зарегистрирован',
                response=UserSerializer,
                examples=[
                    OpenApiExample(
                        'Успешная регистрация',
                        value={
                            "username": "john_doe",
                            "email": "john@example.com",
                            "id": 1,
                            "first_name": "",
                            "last_name": "",
                            "bio": "",
                            "avatar": None,
                            "github_username": "",
                            "date_joined": "2024-01-15T10:00:00Z",
                            "last_login": None,
                            "is_github_user": False
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Ошибка валидации',
                examples=[
                    OpenApiExample(
                        'Пароли не совпадают',
                        value={"password_confirm": ["Пароли не совпадают"]}
                    ),
                    OpenApiExample(
                        'Пользователь существует',
                        value={"username": ["Пользователь с таким именем уже существует"]}
                    )
                ]
            )
        }
    ),
)
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema_view(
    post=extend_schema(
        summary="Вход в систему",
        description="Аутентифицирует пользователя и возвращает данные пользователя",
        tags=['Authentication'],
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Успешный вход',
                response=UserSerializer,
                examples=[
                    OpenApiExample(
                        'Успешная аутентификация',
                        value={
                            "detail": "Успешный вход",
                            "user": {
                                "id": 1,
                                "username": "john_doe",
                                "email": "john@example.com",
                                "first_name": "John",
                                "last_name": "Doe",
                                "bio": "Блогер и разработчик",
                                "avatar": None,
                                "github_username": "johndoe",
                                "date_joined": "2024-01-15T10:00:00Z",
                                "last_login": "2024-01-15T12:00:00Z",
                                "is_github_user": False
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Неверные учетные данные',
                examples=[
                    OpenApiExample(
                        'Неверный пароль',
                        value={"username": ["Неверные учетные данные"]}
                    )
                ]
            )
        }
    ),
)
class LoginView(APIView):
    """Basic authentication"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)

            return Response({
                'detail': 'Успешный вход',
                'user': UserSerializer(user).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        summary="Выход из системы",
        description="Завершает сеанс авторизованного пользователя",
        tags=['Authentication'],
        request=None,
        responses={
            200: OpenApiResponse(
                description='Успешный выход',
                examples=[
                    OpenApiExample(
                        'Успешный выход',
                        value={"detail": "Выход выполнен"}
                    )
                ]
            ),
            403: OpenApiResponse(description='Требуется авторизация')
        }
    ),
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Выход выполнен'})


@extend_schema_view(
    get=extend_schema(
        summary="Получить профиль текущего пользователя",
        description="Возвращает данные профиля авторизованного пользователя",
        tags=['Authentication'],
        request=None,
        responses={
            200: OpenApiResponse(
                description='Данные профиля',
                response=UserSerializer,
                examples=[
                    OpenApiExample(
                        'Успешный ответ',
                        value={
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "bio": "Блогер и разработчик",
                            "avatar": None,
                            "github_username": "johndoe",
                            "date_joined": "2024-01-15T10:00:00Z",
                            "last_login": "2024-01-15T12:00:00Z",
                            "is_github_user": False
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description='Требуется авторизация')
        }
    ),
    put=extend_schema(
        summary="Полностью обновить профиль",
        description="Полностью обновляет профиль авторизованного пользователя",
        tags=['Authentication'],
        request=UserSerializer,
        responses={
            200: OpenApiResponse(description='Профиль успешно обновлен'),
            403: OpenApiResponse(description='Требуется авторизация')
        }
    ),
    patch=extend_schema(
        summary="Частично обновить профиль",
        description="Частично обновляет профиль авторизованного пользователя",
        tags=['Authentication'],
        request=UserSerializer,
        responses={
            200: OpenApiResponse(description='Профиль успешно обновлен'),
            403: OpenApiResponse(description='Требуется авторизация')
        }
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user