from django import forms, template
from datetime import date, timedelta
from django import template

register = template.Library()

@register.filter
def vnd_format(value):
    try:
        value = float(value)
        return "{:,.0f}".format(value).replace(",", ".")
    except:
        return "0"

@register.filter
def sum_total_price(items):
    return sum(item.total_price for item in items)

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except:
        return 0

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except:
        return 0

@register.filter
def sub(value, arg):
    try:
        return float(value) - float(arg)
    except:
        return 0

@register.filter
def tour_status(tour):
    today = date.today()
    start = tour.start_date
    end = start + timedelta(days=tour.duration_days - 1)  # Kết thúc sau duration_days - 1 ngày

    if today < start:
        return "⏳ Sắp bắt đầu"
    elif start <= today <= end:
        return "🚐 Đang diễn ra"
    else:
        return "✅ Đã kết thúc"
@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})
