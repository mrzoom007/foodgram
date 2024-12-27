from django.urls import path, include

urlpatterns = [
    path('users/', include('api.users.urls', namespace='users')),
    path('', include('api.recipes.urls', namespace='recipes')),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
