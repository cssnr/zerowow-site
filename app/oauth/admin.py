from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'guild_member', 'guild_officer', 'is_staff',)
    list_filter = ('guild_member', 'guild_officer', 'is_staff',)
    fieldsets = UserAdmin.fieldsets + (
        ('OAuth', {'fields': ('discord_roles', 'guild_member', 'guild_officer',)}),
    )
    readonly_fields = ('discord_roles',)
    search_fields = ('username',)
    ordering = ('first_name',)


admin.site.register(CustomUser, CustomUserAdmin)
