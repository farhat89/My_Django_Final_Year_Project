from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, css):
    """
    Add CSS classes to form fields
    Usage: {{ form.field|addclass:'form-control' }}
    """
    existing_classes = field.field.widget.attrs.get('class', '')
    if existing_classes:
        # If the field already has classes, append the new ones
        classes = f"{existing_classes} {css}"
    else:
        classes = css
    return field.as_widget(attrs={"class": classes})