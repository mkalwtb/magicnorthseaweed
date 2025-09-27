from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('week/', views.week_overview, name='week_overview'),
    path('spot/<str:spot_name>/', views.spot_table, name='spot_table'),
    path('widget/<str:spot_name>/', views.spot_widget, name='spot_widget'),
    path('health/', views.health_check, name='health_check'),
]


