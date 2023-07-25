from django.contrib import admin
from .models import Event, Person, Boutique
from django.contrib.admin import AdminSite
from django.contrib.admin import SimpleListFilter

# Register your models here.


admin.site.site_header = "Bianco Administration"
admin.site.site_title = "NESchedule"
admin.site.index_title = "Welcome to The NESchedule Portal"



class PersonFilter(admin.ModelAdmin):
    list_display = ('f_name', 'l_name', 'position', 'RTO_days', 'boutique')
    list_filter = ('boutique', 'position')


class EventFilter(admin.ModelAdmin):
    list_display = ('person','type', 'date_start', 'date_end', 'time', 'status', 'boutique')
    list_filter = ('boutique', 'type', 'status')

admin.site.register(Event, EventFilter)
admin.site.register(Person, PersonFilter)
admin.site.register(Boutique)

