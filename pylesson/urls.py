import profile

from django.urls import include, path
from .views import *
urlpatterns = [

    path('',home,name='home'),
    path('index/',index,name='index'),
    path('lesson/<int:pk>',lesson,name='lesson'),
    path('profile/',profile_view,name='profile'),


]