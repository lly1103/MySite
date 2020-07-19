from django.contrib import admin

# Register your models here.
from read_count.models import ReadNum
from read_count.models import ReadDetail


@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('read_num', 'content_object')

@admin.register(ReadDetail)
class ReadDetailAdmin(admin.ModelAdmin):
    list_display = ('date', 'read_num', 'content_object')