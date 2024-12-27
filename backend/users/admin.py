from django.contrib import admin
from users.models import (Follow, User)
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'recipes_count',
        'subscriptions_count'
    )
    list_display_links = ('username',)
    search_fields = ('username',)
    list_filter = ('email',)
    list_editable = (
        'email',
        'first_name',
        'last_name'
    )
    list_fields = ('first_name',)
    empty_value_display = 'Не задано'

    def recipes_count(self, obj):
        return obj.recipe.count()

    recipes_count.short_description = 'Кол-во рецептов'

    def subscriptions_count(self, obj):
        return obj.subscriber.count()

    subscriptions_count.short_description = 'Кол-во подписчиков'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscriber')
    search_fields = ('user', 'subscriber')
    list_filter = ('user', 'subscriber')
    empty_value_display = 'Не задано'
