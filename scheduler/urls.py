from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path("schedule/", views.index_view, name="index"),
    path('create-event/', views.create_event, name='create_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
    path('set_event_status/', views.set_event_status, name='set_event_status'),
    path('quick-approve/<int:pk>/', views.quick_approve, name='quick_approve'),
    path('login/', views.login, name='login'),

    path('', views.redirect_index, name='redirect_index')
]


