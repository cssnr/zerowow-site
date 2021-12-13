from django.contrib import admin
from .models import GuildProfile, GuildNews, GuildApplicants

admin.site.site_header = 'Zero Wow Administration'


@admin.register(GuildProfile)
class GuildProfileAdmin(admin.ModelAdmin):
    list_display = ('main_char', 'main_class', 'main_role', 'show_in_roster', 'id',)
    list_filter = ('main_class', 'main_role', 'show_in_roster',)
    search_fields = ('main_char', 'id',)
    ordering = ('main_char',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(GuildNews)
class GuildNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_name', 'published', 'created_at')
    list_filter = ('published',)
    search_fields = ('title',)
    ordering = ('-created_at',)


@admin.register(GuildApplicants)
class GuildApplicantsAdmin(admin.ModelAdmin):
    list_display = ('char_name', 'char_role', 'raid_1', 'raid_2', 'app_status',)
    list_filter = ('app_status', 'raid_1', 'raid_2', 'char_role',)
    readonly_fields = ('char_name', 'char_role', 'warcraft_logs', 'speed_test', 'spoken_langs', 'native_lang',
                       'raid_1', 'raid_2', 'raid_exp', 'why_join', 'contact_info',)
    search_fields = ('char_name',)
    ordering = ('-pk',)

    def has_add_permission(self, request, obj=None):
        return False
