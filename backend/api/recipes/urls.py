from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagsViewSet, IngredientsViewSet, RecipeViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
