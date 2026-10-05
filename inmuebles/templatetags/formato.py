from django import template

register = template.Library()


@register.filter
def pesos(valor):
    return "$" + f"{int(valor):,}".replace(",", ".")
