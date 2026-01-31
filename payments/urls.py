from django.urls import path

from payments.views import buy_lesson
app_name = 'payments'
urlpatterns = [
# payment/urls.py
    path('buy-lesson/', buy_lesson, name='buy_lesson')

]