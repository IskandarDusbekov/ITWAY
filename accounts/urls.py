from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path("verify-otp/", verify_otp_view, name="verify_otp"),

    # Yangi parolni tiklash url'lari
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password/', reset_password_view, name='reset_password'),
]