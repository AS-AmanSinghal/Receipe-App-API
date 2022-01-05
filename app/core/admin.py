from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin
from django.utils.translation import gettext_lazy as _
from .models import User,Tag,Ingredient


# Register your models here.

class UserAdmin(BaseAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
                    (None, {'fields': ('email', 'password')}),
                    (_('Personal Info'),{'fields':('name',)}),
                )
    add_fieldsets = (
                    (None, {'fields': ('email', 'password1','password2'),
                            'classes':'wide'}),
                    (_('Personal Info'),{'fields':('name',)}),
                )


admin.site.register(User, UserAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)