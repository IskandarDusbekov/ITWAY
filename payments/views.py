from venv import logger

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from payments.models import LessonPurchase, UserBalance, BalanceHistory
from pylesson.models import Lesson


@login_required
@require_POST
def buy_lesson(request):
    try:
        lesson_id = request.POST.get('lesson_id')
        if not lesson_id:
            return JsonResponse({'error': 'Dars ID ko\'rsatilmagan'}, status=400)

        lesson = get_object_or_404(Lesson, id=lesson_id)

        # 1. Agar dars bepul bo'lsa, lekin allaqachon sotib olinsa?
        if not lesson.is_paid:
            # Bepul darsni "sotib olish" emas, balki ro'yxatdan o'tkazish
            purchase, created = LessonPurchase.objects.get_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'price': 0}
            )
            if created:
                return JsonResponse({
                    'success': True,
                    'message': 'Bepul darsga ro\'yxatdan o\'tdingiz'
                })
            else:
                return JsonResponse({
                    'error': 'Bu darsga allaqachon ro\'yxatdan o\'tgansiz'
                }, status=400)

        # 2. Pullik darsni sotib olish
        if LessonPurchase.objects.filter(
            user=request.user,
            lesson=lesson
        ).exists():
            return JsonResponse({
                'error': 'Dars allaqachon sotib olingan'
            }, status=400)

        balance, _ = UserBalance.objects.get_or_create(
            user=request.user,
            defaults={'amount': 0}
        )

        if balance.amount < lesson.price:
            return JsonResponse({
                'error': 'Balans yetarli emas'
            }, status=400)

        with transaction.atomic():
            balance.amount -= lesson.price
            balance.save()

            purchase = LessonPurchase.objects.create(
                user=request.user,
                lesson=lesson,
                price=lesson.price
            )

            BalanceHistory.objects.create(
                user=request.user,
                amount=-lesson.price,
                reason=f"{lesson.title} darsi sotib olindi",
                 # Agar relation bo'lsa
            )

        return JsonResponse({
            'success': True,
            'message': 'Dars muvaffaqiyatli sotib olindi',
            'purchase_id': purchase.id
        })

    except Exception as e:
        # Log qilish
        logger.error(f"buy_lesson error: {str(e)}")
        return JsonResponse({
            'error': 'Server xatosi yuz berdi'
        }, status=500)