from django import template
from django.contrib.contenttypes.models import ContentType

from ..forms import CommentForm
from ..models import Comment


register = template.Library()

@register.simple_tag
def get_comment_count(obj): # 获取评论数量
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()

@register.simple_tag
def get_comment_form(obj):  # 获取评论表单
    content_type = ContentType.objects.get_for_model(obj)
    comment_form = CommentForm(initial={'content_type': content_type.model,
                                        'object_id': obj.pk,
                                        'reply_comment_id': 0})
    return comment_form

@register.simple_tag
def get_comment_list(obj):  # 获取评论列表
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk,
                                      parent=None).order_by('-comment_time')
    return comments

