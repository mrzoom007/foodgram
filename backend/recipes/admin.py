from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    list_editable = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('slug',)
    empty_value_display = 'Не задано'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_editable = ('measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
        'text',
        'image',
        'cooking_time',
    )
    list_editable = ('author',)
    search_fields = (
        'name',
        'author',
        'ingredients'
    )
    list_filter = ('tags',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_editable = ('recipe',)
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = ('user',)
    empty_value_display = 'Не задано'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_editable = ('recipe',)
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = ('user',)
    empty_value_display = 'Не задано'
