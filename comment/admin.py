from django.contrib import admin
# Register your models here.
from comment.models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'text', 'comment_time', 'user')