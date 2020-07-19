
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse

from .forms import CommentForm
from .models import Comment

# Create your views here.
def update_comment(request):
    '''referer = request.META.get('HTTP_REFERER', reverse('home'))
    # 获取评论信息、类型、ID 并数据检查
    if not request.user.is_authenticated:
        return render(request, 'error.html', {'message': '用户验证失败！未登陆', 'redirect_to': referer})
    text = request.POST.get('text', '').strip()
    if text == '':
        return render(request, 'error.html', {'message': '评论内容不能为空！', 'redirect_to': referer})
    try:
        object_id = request.POST.get('object_id')
        content_type = request.POST.get('content_type')  # < ContentType: blog | blog > 得到ContentType字符串类型
        model_class = ContentType.objects.get(model=content_type).model_class() # 将< ContentType: blog | blog > 字符串 转换成 <class 'blog.models.Blog'> blog类对象
        model_obj = model_class.objects.get(pk=object_id)
    except Exception as e:
        return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer})
    # 数据保存
    comment = Comment()
    comment.text = text
    comment.user = request.user
    comment.content_object = model_obj
    comment.save()
    return redirect(referer)'''

    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}

    if comment_form.is_valid():
        # 检查数据 保存数据
        comment = Comment()
        comment.text = comment_form.cleaned_data['text']
        comment.user = comment_form.cleaned_data['user']
        comment.content_object = comment_form.cleaned_data['content_object']

        parent = comment_form.cleaned_data['parent']
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 发送邮件通知
        comment.send_mail()

        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()
        data['comment_time'] = comment.comment_time.timestamp()
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()
        else:
            data['reply_to'] = ''
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''
    else:
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer})
    return JsonResponse(data)