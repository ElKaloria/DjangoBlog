from rest_framework import serializers

from blog.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    amount_of_likes = serializers.SerializerMethodField(method_name='get_amount_of_likes')
    amount_of_comments = serializers.SerializerMethodField(method_name='get_amount_of_comments')

    def get_amount_of_likes(self, obj):
        return obj.likes.count()

    def get_amount_of_comments(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        return post

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()

        return instance

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'author',
            'created_at',
            'updated_at',
            'amount_of_likes',
            'amount_of_comments'
        ]