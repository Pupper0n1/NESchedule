from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path("schedule/", views.index_view, name="index"),
    path('create-event/', views.create_event, name='create_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
    path('', views.redirect_index, name='redirect_index')
]
