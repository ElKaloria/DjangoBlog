from rest_framework import serializers

from blog.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField(source='post.title')
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']