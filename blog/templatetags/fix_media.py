from django import template
from django.conf import settings

register = template.Library()

@register.filter(is_safe=True)
def fix_media(html):
    """
    Fix relative media URLs in stored HTML content
    """
    if not html:
        return html

    # Fix image src
    html = html.replace('src="media/', f'src="{settings.MEDIA_URL}')
    html = html.replace("src='media/", f"src='{settings.MEDIA_URL}")

    return html
