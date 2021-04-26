from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import Agent, User, Category, Product, Manufacturer, Coupon_Dis

class BaseUserAdmin(UserAdmin):
    list_display = ('email', 'is_admin')
    search_fields = ('email',)
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ()
    fieldsets = ()
    list_filter = ()

admin.site.register(User, BaseUserAdmin)
admin.site.register(Agent)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Coupon_Dis)
admin.site.register(Manufacturer)