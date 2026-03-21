from django import template

register = template.Library()


@register.filter
def first_paragraph(text: str | None) -> str:
    """Return the first double-newline-separated paragraph of a text block.

    Used on the homepage to show only the opening paragraph of the design
    philosophy without wrapping the whole multi-paragraph field in a blockquote.
    """
    if not text:
        return ""
    return text.split("\n\n")[0].strip()
