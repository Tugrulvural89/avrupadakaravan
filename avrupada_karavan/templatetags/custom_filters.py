from django import template
import re

register = template.Library()


@register.filter(name='transform_product_url')
def transform_product_url(url):
    if 'suchen.mobile.de/fahrzeuge/details.html?id=' in url:
        match = re.search(r'id=(\d+)', url)
        if match:
            id = match.group(1)
            return f'https://suchen.mobile.de/fahrzeuge/printView.html?id={id}'
    return url

