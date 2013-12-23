from django.contrib import admin
from pipedlyapp.models import LinkedinProfile

class LinkedinAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'url']

admin.site.register(LinkedinProfile, LinkedinAdmin)
