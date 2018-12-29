from django.contrib import admin
from meetup import models

admin.site.register(models.APICredentials)
admin.site.register(models.MeetupCategory)
admin.site.register(models.MeetupLocation)
admin.site.register(models.MeetupGroupFilter)
admin.site.register(models.MeetupGroup)
admin.site.register(models.MeetupUser)
admin.site.register(models.MeetupGroupMember)

