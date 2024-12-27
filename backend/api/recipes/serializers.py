from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from django.shortcuts import get_object_or_404

from backend.constants import (
    MAX_COOKING_TIME, MAX_INGREDIENTS,
    MIN_COOKING_TIME, MIN_INGREDIENTS, NAME_LENGTH)
from recipes.models import (
    Ingredient, IngredientInRecipe, Recipe, ShoppingList, Tag, Favorite
)
from api.users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(
        required=True,
        min_value=MIN_INGREDIENTS,
        max_value=MAX_INGREDIENTS
    )
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='recipes_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ingredients = instance.recipes_ingredients.all()
        data['ingredients'] = IngredientInRecipeSerializer(ingredients,
                                                           many=True).data
        return data

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return request.user.favoriteuser.filter(
                recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return request.user.shoppinglist_users.filter(
                recipe=obj).exists()
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')


class RecipeWriteSerializer(RecipeGetSerializer):
    image = Base64ImageField(required=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='recipes_ingredients')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    def validate(self, data):
        data = super().validate(data)
        request = self.context['request']
        get_tags = request.data.get('tags')
        if not get_tags:
            raise serializers.ValidationError(
                {'tags': ['Обязательное поле.']})
        tags_data = set()
        for tag_data in get_tags:
            try:
                tag = Tag.objects.get(pk=tag_data)
                if tag in tags_data:
                    raise serializers.ValidationError(
                        {'tags': ['Такой тэг уже есть.']})
                tags_data.add(tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'Tag': ['Такого тэга нет.']})
        get_ingredients = request.data.get('ingredients')
        if not get_ingredients:
            raise serializers.ValidationError(
                {'ingredients': ['Обязательное поле.']})
        ingredients_set = set()
        for ingredient in get_ingredients:
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    {'ingredients': ['Такой id занят.']})
            ingredients_set.add(ingredient['id'])
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'ingredients': ['Такого ингредиента нет.']})
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({'image': 'Обязательное поле.'})
        return value

    def create_ingredients(self, ingredients_data, recipe):
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = ingredient_data['amount']
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop('recipes_ingredients')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        ingredients = self.initial_data.get('ingredients')
        self.create_ingredients(ingredients, instance)
        return instance

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('is_favorited', None)
        validated_data.pop('is_in_shopping_cart', None)
        tags_data = validated_data.pop('tags')
        validated_data.pop('recipes_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        ingredients = self.initial_data.get('ingredients')
        self.create_ingredients(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = TagSerializer(instance.tags.all(), many=True).data
        data['is_favorited'] = self.get_is_favorited(instance)
        data['is_in_shopping_cart'] = self.get_is_in_shopping_cart(instance)
        return data


class CropRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    recipes = RecipeGetSerializer(read_only=True)

    def to_representation(self, instance):
        return CropRecipeSerializer(
            instance.recipes, context=self.context).data

    def validate(self, data):
        request = self.context['request']
        recipe_id = self.context['view'].kwargs.get('pk')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST' and request.user.shoppinglist_users.filter(
                recipes=recipe).exists():
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в корзине.']})
        return data

    class Meta:
        model = ShoppingList
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')


class FavoriteSerializer(ShoppingListSerializer):
    def validate(self, data):
        request = self.context['request']
        recipe_id = self.context['view'].kwargs.get('pk')
        if not Recipe.objects.filter(pk=recipe_id).exists():
            raise serializers.ValidationError(
                {'recipes': ['Такого рецепта нет.']})
        if request.method == 'POST' and request.user.favorite_users.filter(
                recipes__id=recipe_id).exists():
            raise serializers.ValidationError(
                {'recipes': ['Рецепт уже в избранном.']})

        return data

    class Meta:
        model = Favorite
        fields = ('recipes',)
        read_only_fields = ('user', 'recipes')
