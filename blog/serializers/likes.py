from rest_framework import serializers

from blog.models import Like


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.ReadOnlyField(source='post.title')
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']

