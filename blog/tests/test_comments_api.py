from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blog.models import Post, Comment, CustomUser


class CommentCreateAPITestCase(APITestCase):
    """Тесты для создания комментариев"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser', email='other@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.url = reverse('comment-create-comment', kwargs={'post_pk': self.post.pk})

    def test_create_comment_authenticated(self):
        """Тест создания комментария авторизованным пользователем"""
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Test comment content'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data['content'], 'Test comment content')
        self.assertEqual(response.data['author'], 'testuser')

    def test_create_comment_unauthenticated(self):
        """Тест создания комментария неавторизованным пользователем"""
        data = {'content': 'Test comment content'}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment_missing_content(self):
        """Тест создания комментария без контента"""
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_for_nonexistent_post(self):
        """Тест создания комментария к несуществующему посту"""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-create-comment', kwargs={'post_pk': 9999})
        data = {'content': 'Test comment'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentListAPITestCase(APITestCase):
    """Тесты для получения списка комментариев"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 1'
        )
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Comment 2'
        )
        self.url = reverse('comment-get-comments', kwargs={'post_pk': self.post.pk})

    def test_list_comments(self):
        """Тест получения списка комментариев к посту"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_comments_for_nonexistent_post(self):
        """Тест получения комментариев к несуществующему посту"""
        url = reverse('comment-get-comments', kwargs={'post_pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_comments_empty(self):
        """Тест получения списка комментариев к посту без комментариев"""
        other_post = Post.objects.create(
            title='Empty Post',
            content='No comments',
            author=self.user
        )
        url = reverse('comment-get-comments', kwargs={'post_pk': other_post.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class CommentUpdateAPITestCase(APITestCase):
    """Тесты для обновления комментариев"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser', email='other@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Original content'
        )
        self.url = reverse('comment-update-comment', kwargs={
            'post_pk': self.post.pk,
            'comment_pk': self.comment.pk})

    def test_update_comment_as_author(self):
        """Тест обновления комментария автором"""
        self.client.force_authenticate(user=self.user)
        data = {'content': 'Updated content'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated content')

    def test_update_comment_as_other_user(self):
        """Тест обновления комментария другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        data = {'content': 'Hacked content'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Original content')

    def test_update_comment_unauthenticated(self):
        """Тест обновления комментария неавторизованным пользователем"""
        data = {'content': 'Hacked content'}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_missing_content(self):
        """Тест обновления комментария без контента"""
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.patch(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_nonexistent_comment(self):
        """Тест обновления несуществующего комментария"""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-update-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': 9999})
        data = {'content': 'Updated content'}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentDeleteAPITestCase(APITestCase):
    """Тесты для удаления комментариев"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser', email='other@example.com', password='Pass123!'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        self.url = reverse('comment-delete-comment', kwargs={
            'post_pk': self.post.pk,
            'comment_pk': self.comment.pk
        })

    def test_delete_comment_as_author(self):
        """Тест удаления комментария автором"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_as_other_user(self):
        """Тест удаления комментария другим пользователем"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment_unauthenticated(self):
        """Тест удаления комментария неавторизованным пользователем"""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_nonexistent_comment(self):
        """Тест удаления несуществующего комментария"""
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-delete-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': 9999})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)