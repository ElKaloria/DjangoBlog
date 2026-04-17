from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True, verbose_name='Biography')
    avatar = models.URLField(blank=True, verbose_name='Avatar')

    github_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='GitHub ID'
    )
    github_username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='GitHub Username'
    )
    github_access_token = models.TextField(blank=True, verbose_name='GitHub Token')

    @property
    def is_github_user(self):
        return bool(self.github_id)

    def get_display_name(self):
        return self.get_full_name() or self.username or self.email

    def __str__(self):
        return self.username or self.email

    class Meta:
        db_table = 'blog_user'
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'