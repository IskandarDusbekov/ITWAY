from django.contrib import admin
from .models import UserBalance, Payment, LessonPurchase, BalanceHistory

# ---------------------------
# UserBalance
# ---------------------------
@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'updated')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('updated',)  # updated fieldni tahrirlamaslik
    ordering = ('-amount',)

# ---------------------------
# Payment
# ---------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'method', 'status', 'created')
    list_filter = ('status', 'method', 'created')
    search_fields = ('user__email', 'user__full_name')
    ordering = ('-created',)
    readonly_fields = ('created',)

# ---------------------------
# LessonPurchase
# ---------------------------
@admin.register(LessonPurchase)
class LessonPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'price', 'created')
    list_filter = ('lesson', 'created')
    search_fields = ('user__email', 'user__full_name', 'lesson__title')
    ordering = ('-created',)
    readonly_fields = ('created',)
    # unique_together = ('user', 'lesson') — bu model Meta da belgilangan, adminda alohida yozish shart emas

# ---------------------------
# BalanceHistory
# ---------------------------
@admin.register(BalanceHistory)
class BalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'reason', 'created')
    list_filter = ('created',)
    search_fields = ('user__email', 'user__full_name', 'reason')
    ordering = ('-created',)
    readonly_fields = ('created',)
