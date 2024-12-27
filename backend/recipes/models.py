from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from recipes.constants import (
    INGREDIENT_LENGTH, MAX_COOKING_TIME, MAX_INGREDIENTS,
    MEASURMENT_LENGTH, MIN_COOKING_TIME, MIN_INGREDIENTS,
    RECIPE_LENGTH, SLUG_LENGTH, TAG_LENGTH
)


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=INGREDIENT_LENGTH,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=MEASURMENT_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тэг (название)',
        unique=True,
        max_length=TAG_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=SLUG_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=RECIPE_LENGTH,
        unique=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        verbose_name='Изображение рецепта',
        upload_to='recipes/',
        null=True,
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(MIN_COOKING_TIME,
                                      message='Не менее 1 минуты.'),
                    MaxValueValidator(MAX_COOKING_TIME,
                                      message='Не более 32000 минут.')
                    ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredients_in_recipes',
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_INGREDIENTS,
                              message='Добавьте хотя бы 1 ингредиент.'),
            MaxValueValidator(MAX_INGREDIENTS,
                              message='Не более 32000 ингредиентов.')
        ],
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_IngredientInRecipe'), ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favoriteuser',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorite recipe for user')
        ]


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppinglist_users',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppinglist_recipes',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт "{self.recipe}" в Корзину'
