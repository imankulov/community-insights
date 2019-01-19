from django.contrib import admin
from meetup import models

admin.site.register(models.APICredentials)
admin.site.register(models.MeetupCategory)
admin.site.register(models.MeetupLocation)
admin.site.register(models.MeetupGroupFilter)


@admin.register(models.MeetupGroup)
class MeetupGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created_date', 'members')
    list_filter = ('city', 'created')
    search_fields = ['name', 'description']

    def created_date(self, obj):
        return obj.created.strftime('%d %b %Y')

    created_date.admin_order_field = 'created'


@admin.register(models.MeetupUser)
class MeetupUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'joined')
    list_filter = ('joined', 'country', 'city')
    search_fields = ['name']



@admin.register(models.MeetupGroupMember)
class MeetupGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'group_name', 'created', 'updated', 'visited')
    list_filter = ('group__name', 'group__city')
    search_fields = ['user__name']

    def user_name(self, obj):
        return obj.user.name

    user_name.admin_order_field = 'user__name'

    def group_name(self, obj):
        return obj.group.name

    group_name.admin_order_field = 'group__name'
