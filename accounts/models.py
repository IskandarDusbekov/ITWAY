from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import secrets


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email




# OTP modeli




class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    token = models.CharField(max_length=64, default=secrets.token_urlsafe, unique=True)
    email = models.EmailField()

    is_expired = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    tries = models.IntegerField(default=0)

    extra = models.JSONField(default=dict)

    class OtpType(models.IntegerChoices):
        LOGIN = 1, "login"
        REGISTER = 2, "register"

    by = models.SmallIntegerField(choices=OtpType.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.tries >= 3:
            self.is_expired = True
        if self.is_confirmed:
            self.is_expired = False
        super().save(*args, **kwargs)

    def check_time(self):
        return (timezone.now() - self.created_at).total_seconds() < 180
