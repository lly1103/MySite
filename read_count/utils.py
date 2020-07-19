import datetime

from django.db.models import Sum
from django.utils import timezone
from read_count.models import ReadNum, ReadDetail
from django.contrib.contenttypes.models import ContentType


def read_count_once(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '{}_{}_read'.format(ct.model, obj.pk)
    if not request.COOKIES.get(key):
        '''
        if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk) # 存在记录 说明已经实例化 取出相应的对象
        else:
            readnum = ReadNum(content_type=ct, object_id=obj.pk) # 不存在对因的记录 实例化模型
        '''
        # 总阅读数加一
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1   # 计数加一
        readnum.save()  # 保存到数据库
        ''''
        if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk).count():
            readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=date)
        else:
            readDetail = ReadDetail(content_type=ct, object_id=obj.pk, date=date)
        '''
        # 当天阅读数加一
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key

# 前七天阅读量统计方法
def get_seven_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_sums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))
        read_sums.append(result['read_num_sum'] or 0)
    return dates, read_sums

# 当天热门博客数据方法
def get_day_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')
    return read_details[:7]

# 昨天天热门博客数据方法
def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')
    return read_details[:7]

'''
# 前七天热门博客数据方法
def get_seven_hot_data(content_type):
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    read_details = ReadDetail.objects.filter(content_type=content_type, date__lt=today, date__gte=date)\
        .values('content_type', 'object_id').annotate(read_num_sum=Sum('read_num')).order_by('-read_num_sum')
    return read_details[:7]
'''