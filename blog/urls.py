from rest_framework.routers import SimpleRouter

from blog.api import (
    PostViewSet,
    LikeViewSet,
    CommentViewSet,
)

blog_router = SimpleRouter()

blog_router.register('posts', PostViewSet, basename='post')
blog_router.register('likes', LikeViewSet, basename='like')
blog_router.register('comments', CommentViewSet, basename='comment')
