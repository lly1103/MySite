import datetime
from django.core.cache import cache
from django.db.models import Sum
from django.shortcuts import render, redirect, reverse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from blog.models import Blog
from read_count.utils import get_seven_read_data, get_day_hot_data, get_yesterday_hot_data

# 前七天热门博客数据方法
def get_seven_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    read_details = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date)\
        .values('title', 'id').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return read_details[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    detes, read_sums = get_seven_read_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    seven_hot_datas = cache.get('seven_hot_datas')
    print(seven_hot_datas)
    if seven_hot_datas is None:
        seven_hot_datas = get_seven_hot_data()
        print(seven_hot_datas[0])
        cache.set('seven_hot_datas ', seven_hot_datas, 3600)
        print("计算")
    else:
        print("使用缓存")

    today_hot_datas = get_day_hot_data(blog_content_type)
    yesterday_hot_datas = get_yesterday_hot_data(blog_content_type)
    seven_hot_datas = get_seven_hot_data()
    return render(request, 'home.html',
                  {'read_sums': read_sums, 'dates': detes, 'today_hot_datas': today_hot_datas,
                   'yesterday_hot_datas': yesterday_hot_datas, 'seven_hot_datas': seven_hot_datas})

