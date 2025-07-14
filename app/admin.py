# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import Place, Food, Culture, Tour, Contact, Review, Order, OrderItem

# 🔁 Bước 1: Bỏ User default
admin.site.unregister(User)

# 👤 Bước 2: Custom UserAdmin để cấp quyền và phân quyền riêng
@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email')

    # ⛔ Chỉ superuser mới chỉnh được các trường đặc quyền
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            for field in ['is_staff', 'is_superuser', 'user_permissions']:
                if field in form.base_fields:
                    form.base_fields[field].disabled = True
        return form

    # 👥 Staff chỉ được xem user trong cùng nhóm
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(groups__in=request.user.groups.all())

# ✅ Bước 3: Đăng ký các model còn lại vào Admin
admin.site.register(Place)
admin.site.register(Food)
admin.site.register(Culture)
admin.site.register(Tour)
admin.site.register(Contact)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
