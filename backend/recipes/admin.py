from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingList, Tag)
from users.models import (Follow, User)

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
