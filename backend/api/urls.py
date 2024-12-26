from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import UserViewSet

from api.views import IngredientsViewSet, RecipeViewSet, TagsViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
