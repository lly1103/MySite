from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
from likes.models import LikeRecord, LikeCount

def errorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)

def successResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)


def like_change(request):
    # 获取数据
    user = request.user
    if not user.is_authenticated:
        return errorResponse(400, 'you were not login 您没有登录')

    content_type = request.GET.get('content_type')
    object_id = int(request.GET.get('object_id'))
    try:
        content_type = ContentType.objects.get(model=content_type)
        model_class = content_type.model_class()
        model_object = model_class.objects.get(pk=object_id)
    except ObjectDoesNotExist:
        return errorResponse(401, 'object not exist 对象不存在')

    # 处理数据
    if request.GET.get('is_like') == 'true':
        # 要点赞模型实例化
        like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id, user=user)
        if created:
            # 未点过赞，进行点赞  点赞计数实例化
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            like_count.liked_num += 1
            like_count.save()
            return successResponse(like_count.liked_num)
        else:
            # 以点过赞，不能重复点赞
            return errorResponse(402, 'you are liked 您已经点过赞了')
    else:
        # 要取消点赞 判断点赞记录是否存在
        if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
            # 有点赞过，取消点赞
            like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
            like_record.delete()
            # 点赞总数减一
            like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
            if not created:
                like_count.liked_num -= 1
                like_count.save()
                return successResponse(like_count.liked_num)
            else:
                return errorResponse(404, 'data error 数据错误')
        else:
            # 没有点赞过，不能取消
            return errorResponse(403, 'you are not liked 您没有点赞')