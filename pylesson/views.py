from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect

from payments.models import LessonPurchase
from pylesson.models import Lesson, Modul


# Create your views here.
@login_required(login_url='/login/')
def index(request):
    ctgs = Modul.objects.filter(
        is_active=True,
        is_menu=True
    ).prefetch_related('lessons')

    total_lessons = Lesson.objects.count()
    total_time = Lesson.objects.aggregate(total=Sum('time'))['total'] or 0

    hours = total_time // 60
    minutes = total_time % 60

    user_purchased_ids = set(
        LessonPurchase.objects.filter(
            user=request.user
        ).values_list('lesson_id', flat=True)
    )

    return render(request, 'index.html', {
        'ctgs': ctgs,
        'total_lessons': total_lessons,
        'hours': hours,
        'minutes': minutes,
        'user_purchased_ids': user_purchased_ids,
    })


@login_required
def lesson(request, pk):
    lesson = get_object_or_404(Lesson, id=pk)
    user = request.user

    # Foydalanuvchi sotib olgan barcha dars ID'lari
    user_purchased_ids = set(
        LessonPurchase.objects.filter(
            user=user
        ).values_list('lesson_id', flat=True)
    )

    # 🔒 AGAR DARS PULLIK BO'LSA VA SOTIB OLINMAGAN BO'LSA
    if lesson.is_paid and lesson.id not in user_purchased_ids:
        return render(request, 'locked.html', {
            'lesson': lesson
        })

    # ✅ FAQAT POST BO'LGANDA YAKUNLASH
    if request.method == "POST":
        if user not in lesson.completed_by.all():
            lesson.completed_by.add(user)
        return redirect('lesson', pk)

    ctgs = Modul.objects.filter(
        is_active=True,
        is_menu=True
    ).prefetch_related('lessons')

    return render(request, 'lesson.html', {
        'ctgs': ctgs,
        'lesson': lesson,
        'user_purchased_ids': user_purchased_ids  # ✅ BU YERDA QO'SHING
    })
@login_required
def profile_view(request):
    user = request.user

    # User balansini olish
    try:
        user_balance = user.balance.amount
    except:
        user_balance = 0

    # Sotib olingan darslar
    purchased_lessons = LessonPurchase.objects.filter(user=user).select_related('lesson', 'lesson__modul')

    # Umumiy sotib olingan darslar soni
    total_purchased = purchased_lessons.count()

    # Umumiy o'qish vaqti (daqiqada)
    total_study_time = purchased_lessons.aggregate(
        total_time=Sum('lesson__time')
    )['total_time'] or 0

    # Sarflangan summa
    total_spent = purchased_lessons.aggregate(
        total_spent=Sum('price')
    )['total_spent'] or 0

    # So'ngi 2 ta sotib olingan dars
    recent_purchases = purchased_lessons.order_by('-created')[:2]

    # Ketma-ket login kunlari (demo uchun)
    streak_days = 12  # Bu haqiqiy loyihada hisoblash kerak

    # Formatlash
    total_study_hours = total_study_time // 60
    total_study_minutes = total_study_time % 60

    context = {
        'user': user,
        'balance': user_balance,
        'total_purchased': total_purchased,
        'total_study_time': total_study_time,
        'total_study_hours': total_study_hours,
        'total_study_minutes': total_study_minutes,
        'total_spent': total_spent,
        'recent_purchases': recent_purchases,
        'streak_days': streak_days,
    }

    return render(request, 'profile.html', context)



def home(request):
    return render(request, 'home.html')