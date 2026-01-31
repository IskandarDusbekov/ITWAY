from django.conf import settings
from django.db import models


class UserBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='balance'
    )
    amount = models.PositiveIntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.amount} so‘m"


class Payment(models.Model):
    STATUS = (
        ('pending', 'Kutilmoqda'),
        ('success', 'Muvaffaqiyatli'),
        ('failed', 'Bekor'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    method = models.CharField(max_length=30)  # click / payme / manual
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    created = models.DateTimeField(auto_now_add=True)



class LessonPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey('pylesson.Lesson', on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')


class BalanceHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()  # + yoki -
    reason = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
