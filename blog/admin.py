from django.contrib import admin
from blog.models import Blog, BlogType


# Register your models here.
@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'blog_type', 'auther', 'get_read_num', 'created_time', 'last_update_time')
