from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'is_staff',)
    list_filter = ('is_staff',)
    fieldsets = UserAdmin.fieldsets + (
        ('OAuth', {'fields': ('id', 'discord_roles', 'guild_member', 'guild_officer',)}),
    )
    readonly_fields = ('discord_roles',)
    search_fields = ('username', 'id',)
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
