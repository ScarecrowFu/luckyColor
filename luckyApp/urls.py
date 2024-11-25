from django.urls import path
from . import views

app_name = 'luckyApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history, name='history'),
    path('random/', views.random_number, name='random'),
    path('predict/', views.predict, name='predict'),
] 