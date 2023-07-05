from django.contrib import admin
from .models import Event, Person
from django.contrib.admin import AdminSite

# Register your models here.
admin.site.register(Event)
admin.site.register(Person)

admin.site.site_header = "Bianco Administration"
admin.site.site_title = "NESchedule"
admin.site.index_title = "Welcome to The NESchedule Portal"