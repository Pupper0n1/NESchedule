from django.urls import path
from . import views

app_name = 'scheduler'

urlpatterns = [
    path('home/', views.home, name='home'),
    path("schedule/<int:pk>/", views.index_view, name="index"),
    path('create-event/', views.create_event, name='create_event'),
    path('delete-event/', views.delete_event, name='delete_event'),
    path('set_event_status/', views.set_event_status, name='set_event_status'),
    path('quick-approve/<int:pk>/', views.quick_approve, name='quick_approve'),
    path('quick-reject/<int:pk>/', views.quick_reject, name='quick_reject'),
    path('login/<int:pk>', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    path('reset-password/', views.reset_password, name='reset_password'),

    path('email-reset-form/', views.email_reset_form, name='email_reset_form'),

    path('reset-password-form/<int:pk>/<str:passwd>/', views.new_password_form, name='reset_password_form'),

    path('new_password_and_redirect/', views.reset_password_and_redirect, name='new_password_and_redirect'),

    path('', views.redirect_index, name='redirect_index')       # This is a redirect to the index page
]


