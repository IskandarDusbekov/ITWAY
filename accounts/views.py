from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Otp
from .utils import generate_key, code_decoder
import random
import uuid
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.hashers import make_password


# ----------------------
# EXISTING LOGIN VIEW (o'zgarishsiz)
# ----------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email yoki parol noto'g'ri!")
            return redirect("login")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.full_name or user.email}!")
                return redirect("index")
            else:
                # OTP tasdiqlanmagan user uchun sessionda saqlaymiz
                request.session["otp_user_id"] = user.id
                messages.error(request, "Emailingiz tasdiqlanmagan! Avval OTP tasdiqlang.")
                return redirect("verify_otp")
        else:
            messages.error(request, "Email yoki parol noto'g'ri!")
            return redirect("login")

    return render(request, "auth/login.html")


# ----------------------
# EXISTING REGISTER VIEW (o'zgarishsiz)
# ----------------------
def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "Parollar mos kelmadi!")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Bu email bilan foydalanuvchi mavjud!")
            return redirect("register")

        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            is_active=False
        )

        code = random.randint(100_000, 999_999)
        otp_token = f"{uuid.uuid4()}${code}${generate_key()}"
        otp_shifr = code_decoder(otp_token, l=3)

        Otp.objects.create(
            user=user,
            email=email,
            token=otp_token,
            by=2,  # register
            extra={"shifr": otp_shifr}
        )

        send_mail(
            subject="Sizning OTP kodingiz",
            message=f"Sizning OTP kodingiz: {code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        request.session["otp_user_id"] = user.id
        messages.success(request, "Emailga OTP yuborildi!")
        return redirect("verify_otp")

    return render(request, "auth/register.html")


# ----------------------
# EXISTING VERIFY OTP VIEW (o'zgarishsiz)
# ----------------------
def verify_otp_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Avval register qiling")
        return redirect("register")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        try:
            otp_obj = Otp.objects.filter(
                user_id=user_id,
                is_expired=False,
                is_confirmed=False
            ).latest("created_at")

            code_from_token = otp_obj.token.split('$')[1]

            if str(otp_input) != str(code_from_token):
                otp_obj.tries += 1
                if otp_obj.tries >= 3:
                    otp_obj.is_expired = True
                otp_obj.save()
                messages.error(request, "Kod noto'g'ri!")
                return redirect("verify_otp")

            if (timezone.now() - otp_obj.created_at).total_seconds() > 180:
                otp_obj.is_expired = True
                otp_obj.save()
                messages.error(request, "OTP muddati tugagan!")
                return redirect("verify_otp")

            otp_obj.is_confirmed = True
            otp_obj.save()

            user = otp_obj.user
            user.is_active = True
            user.save()

            messages.success(request, "Email tasdiqlandi!")
            request.session.pop("otp_user_id", None)
            return redirect("login")

        except Otp.DoesNotExist:
            messages.error(request, "OTP mavjud emas yoki expired!")

    return render(request, "auth/verify_otp.html")


# ----------------------
# YANGI: PAROLNI UNUTISH VIEW
# ----------------------
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            # OTP yaratish va yuborish
            code = random.randint(100_000, 999_999)
            otp_token = f"{uuid.uuid4()}${code}${generate_key()}"
            otp_shifr = code_decoder(otp_token, l=3)

            # OTP bazaga saqlash (by=3 - password reset uchun)
            Otp.objects.create(
                user=user,
                email=email,
                token=otp_token,
                by=3,  # password reset
                extra={"shifr": otp_shifr, "type": "password_reset"}
            )

            # Email yuborish
            send_mail(
                subject="Parolni tiklash uchun OTP kodi",
                message=f"Parolingizni tiklash uchun OTP kodingiz: {code}\n"
                        f"Bu kod faqat 3 daqiqa davomida amal qiladi.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )

            # Sessionga user emailini saqlash
            request.session["reset_password_email"] = email
            messages.success(request, f"Parolni tiklash uchun OTP kodi {email} manziliga yuborildi!")
            return redirect("verify_reset_otp")

        except User.DoesNotExist:
            messages.error(request, "Bu email bilan foydalanuvchi topilmadi!")
            return redirect("forgot_password")

    return render(request, "auth/forgot_password.html")


# ----------------------
# YANGI: RESET PASSWORD OTP TASDIQLASH VIEW
# ----------------------
def verify_reset_otp_view(request):
    email = request.session.get("reset_password_email")
    if not email:
        messages.error(request, "Avval parolni tiklash so'rovini yuboring")
        return redirect("forgot_password")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_obj = Otp.objects.filter(
                user=user,
                email=email,
                by=3,  # password reset
                is_expired=False,
                is_confirmed=False
            ).latest("created_at")

            code_from_token = otp_obj.token.split('$')[1]

            if str(otp_input) != str(code_from_token):
                otp_obj.tries += 1
                if otp_obj.tries >= 3:
                    otp_obj.is_expired = True
                otp_obj.save()
                messages.error(request, "Kod noto'g'ri!")
                return redirect("verify_reset_otp")

            if (timezone.now() - otp_obj.created_at).total_seconds() > 180:
                otp_obj.is_expired = True
                otp_obj.save()
                messages.error(request, "OTP muddati tugagan!")
                return redirect("verify_reset_otp")

            # OTP tasdiqlash
            otp_obj.is_confirmed = True
            otp_obj.save()

            # Yangi session key yaratish
            reset_token = str(uuid.uuid4())
            request.session["reset_token"] = reset_token
            request.session["verified_email"] = email
            messages.success(request, "OTP tasdiqlandi! Endi yangi parol o'rnating.")
            return redirect("reset_password")

        except (User.DoesNotExist, Otp.DoesNotExist):
            messages.error(request, "OTP mavjud emas yoki xato!")
            return redirect("verify_reset_otp")

    return render(request, "auth/verify_reset_otp.html")


# ----------------------
# YANGI: YANGI PAROL O'RNATISH VIEW
# ----------------------
def reset_password_view(request):
    email = request.session.get("verified_email")
    reset_token = request.session.get("reset_token")

    if not email or not reset_token:
        messages.error(request, "Avval OTP kodni tasdiqlang")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Parollar mos kelmadi!")
            return redirect("reset_password")

        try:
            user = User.objects.get(email=email)

            # Parolni o'zgartirish
            user.password = make_password(new_password)
            user.save()

            # Sessionni tozalash
            request.session.pop("reset_password_email", None)
            request.session.pop("verified_email", None)
            request.session.pop("reset_token", None)

            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi! Endi login qilishingiz mumkin.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "Foydalanuvchi topilmadi!")
            return redirect("reset_password")

    return render(request, "auth/reset_password.html")


# ----------------------
# YANGI: LOGOUT VIEW
# ----------------------
def logout_view(request):
    logout(request)
    messages.success(request, "Siz tizimdan chiqdingiz!")
    return redirect("login")