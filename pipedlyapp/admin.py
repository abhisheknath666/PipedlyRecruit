from django.contrib import admin
from pipedlyapp.models import Poll, Choice, LinkedinProfile

class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3

class PollAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]

    inlines = [ChoiceInline]

class LinkedinAdmin(admin.ModelAdmin):
    fields = ['first_name', 'last_name', 'url']

admin.site.register(Poll, PollAdmin)
admin.site.register(LinkedinProfile, LinkedinAdmin)
