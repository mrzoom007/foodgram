from django.contrib.auth import hashers
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint
from django.utils.translation import gettext_lazy
from rest_framework.exceptions import ValidationError

from backend.constants import (EMAIL_LENGTH, NAME_LENGTH, ROLE_LENGTH)


def user_validator(value):
    if value == 'me':
        raise ValidationError('Неверный логин')


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'username',
    ]

    class Roles(models.TextChoices):
        ADMIN = 'admin', gettext_lazy('Admin')
        USER = 'user', gettext_lazy('User')

    username = models.CharField(
        'Логин',
        max_length=NAME_LENGTH,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Ошибка валидации'
        )],
    )
    first_name = models.CharField(
        'Имя',
        max_length=NAME_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=NAME_LENGTH
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        null=True,
        blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=ROLE_LENGTH,
        default=Roles.USER,
        choices=Roles.choices,
    )

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    class Meta:
        ordering = ['username', 'email']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def set_password(self, set_pass):
        self.password = hashers.make_password(set_pass)

    def update_password(self, old_pass, new_pass):
        if not self.check_password(old_pass):
            raise ValueError('Неверный пароль.')
        self.set_password(new_pass)
        self.save()

    def check_password(self, check_pass):
        return hashers.check_password(check_pass, self.password)

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN or self.is_superuser

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscription_author',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    subscriber = models.ForeignKey(
        User,
        related_name='subscribers',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(fields=['user', 'subscriber'],
                             name='unique_subscribers'),
            CheckConstraint(
                name='self_subscribing_constraint',
                check=~models.Q(user=models.F('subscriber')),
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.user}'

    def clean(self):
        if self.user == self.subscriber:
            raise ValidationError('Нельзя подписаться на себя')
