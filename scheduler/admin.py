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
    search_fields = ('f_name', 'l_name', 'boutique__name', 'boutique__city', 'boutique__province')

 

 
class EventFilter(admin.ModelAdmin):
    list_display = ('person','type', 'date_start', 'date_end', 'time', 'status', 'boutique')
    list_filter = ('boutique', 'type', 'status')
    search_fields = ('person__f_name', 'person__l_name', 'type', 'boutique__name', 'boutique__city', 'boutique__province')

admin.site.register(Event, EventFilter)
admin.site.register(Person, PersonFilter)
admin.site.register(Boutique)

