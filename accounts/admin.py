from django.contrib import admin
from .models import Profile
# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'user_group']
    search_fields = ['user__username', 'user__group__name']
    list_filter = ['user__groups', 'user__username']

    def user_group(self, obj):
        return '-'.join([g.name for g in obj.user.groups.all().order_by('name')])

    user_group.short_description = 'Grupo'


admin.site.register(Profile, ProfileAdmin)
