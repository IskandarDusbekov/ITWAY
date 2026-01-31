from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField




class Modul(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_menu = models.BooleanField(default=True)   # menyuda ko‘rinadimi
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    modul = models.ForeignKey(Modul, on_delete=models.CASCADE, related_name='lessons')
    video_id = models.CharField(max_length=400,null=True,blank=True,default="cNGjD0VG4R8")
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    about = RichTextField()          # qisqacha tavsif
    lesson_text = RichTextField()    # dars matni / qo‘shimcha info
    time = models.PositiveIntegerField(help_text="Vaqt (daqiqa)")  # faqat musbat son
    likes = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)  # pullik dars
    price =models.PositiveIntegerField(default=0)
    completed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='completed_lessons',

    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def can_access(self, user):
        if not self.is_paid:
            return True
        return user.purchased_lessons.filter(id=self.id).exists()

    def __str__(self):
        return f"{self.modul.name} - {self.title}"

