from django_filters import FilterSet, filters


from blog.models import Post

class PostFilter(FilterSet):
    author = filters.CharFilter(field_name='author__username')
    created_at = filters.DateFilter(field_name='created_at')

    ordering = filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('author', 'author'),
            ('likes_count', 'likes_count'),
            ('comments_count', 'comments_count'),
        )
    )

    class Meta:
        model = Post
        fields = {
            'author': ['exact'],
            'created_at': ['exact'],
        }