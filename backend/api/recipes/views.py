from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import (
    SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework import status, viewsets
from rest_framework.decorators import action

from api.recipes.filters import AuthorAndTagFilter, IngredientSearchFilter
from api.pagination import LimitPageNumberPagination
from api.permissions import IsOwnerOrReadOnly
from api.recipes.serializers import (
    CropRecipeSerializer, IngredientSerializer,
    TagSerializer,
    RecipeWriteSerializer, RecipeGetSerializer)
from recipes.models import (
    ShoppingList, Favorite, Ingredient, Recipe, Tag
)
from recipes.services.generate_shopping_cart import generate_shopping_cart_pdf


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorAndTagFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self.add_obj(Favorite, request.user, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        return self.delete_obj(Favorite, request.user, pk)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.add_obj(ShoppingList, request.user, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        return self.delete_obj(ShoppingList, request.user, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        return generate_shopping_cart_pdf(request.user)

    def add_obj(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = CropRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = get_object_or_404(model, user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        get_object_or_404(Recipe, id=pk)
        url = request.build_absolute_uri(f'/recipes/{pk}/')
        return Response({'short-link': url}, status=status.HTTP_200_OK)
