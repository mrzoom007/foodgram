from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer
)
from users.constants import (NAME_LENGTH)

from recipes.models import Recipe
from users.models import Follow, User


class UserCreateSerializer(DjoserUserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()),
                    RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username contains restricted symbols. Please use only '
                    'letters, numbers and .@+- symbols',
        ), ],
        max_length=NAME_LENGTH)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ReadOnlyField(source='user.avatar_url')

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            subscriber=obj.subscriber, user=obj.user
        ).exists()

    def get_recipes(self, obj):
        from api.recipes.serializers import CropRecipeSerializer
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.user)
        if limit:
            queryset = queryset[:int(limit)]
        return CropRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.user).count()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.subscribers.filter(user=obj).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        required_fields = ('username', 'first_name', 'last_name')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    def update(self, instance, validated_data):
        avatar_data = validated_data.get('avatar', None)
        file_avatar = ContentFile(avatar_data.read())
        instance.avatar.save('image.png', file_avatar, save=True)
        return instance

    def validate_avatar(self, avatar_data):
        if not avatar_data:
            raise serializers.ValidationError('Пустой запрос.')
        return avatar_data

    class Meta:
        model = User
        fields = ('avatar',)
