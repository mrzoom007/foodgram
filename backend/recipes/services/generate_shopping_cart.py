from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from recipes.models import IngredientInRecipe


def generate_shopping_cart_pdf(user):
    final_list = {}
    ingredients = IngredientInRecipe.objects.filter(
        recipe__shoppinglist_recipes__user=user
    ).values_list(
        'ingredient__name', 'ingredient__measurement_unit', 'amount'
    )
    for item in ingredients:
        name = item[0]
        if name not in final_list:
            final_list[name] = {
                'measurement_unit': item[1],
                'amount': item[2]
            }
        else:
            final_list[name]['amount'] += item[2]

    pdfmetrics.registerFont(
        TTFont('Slimamif', 'Slimamif.ttf', 'UTF-8')
    )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.pdf"'
    )
    page = canvas.Canvas(response)
    page.setFont('Slimamif', size=24)
    page.drawString(200, 800, 'Список ингредиентов')
    page.setFont('Slimamif', size=16)
    height = 750
    for i, (name, data) in enumerate(final_list.items(), 1):
        page.drawString(
            75, height,
            f'<{i}> {name} - {data["amount"]}, {data["measurement_unit"]}'
        )
        height -= 25
    page.showPage()
    page.save()

    return response
