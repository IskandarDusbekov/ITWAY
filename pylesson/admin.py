from django.contrib import admin

# Register your models here.
# app_name/admin.py
from django.contrib import admin
from .models import Modul, Lesson


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',

        'is_menu',
        'is_active',
        'created',
    )
    list_display_links = ('id', 'name')
    list_filter = ( 'is_menu', 'is_active', 'created')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created',)
    list_editable = ( 'is_menu', 'is_active')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'modul',
        'is_paid',
        'time',
        'likes',
        'created',
        'updated',
    )
    list_display_links = ('id', 'title')
    list_filter = ('modul', 'is_paid', 'created')
    search_fields = ('title', 'about', 'lesson_text')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created',)
    list_editable = ('is_paid', 'time')



