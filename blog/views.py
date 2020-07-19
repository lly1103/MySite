from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from read_count.utils import read_count_once
from MySite import settings
from blog.models import Blog, BlogType

def blog_common_data(request, blogs_all_list):
    blog_dates = Blog.objects.dates('created_time', 'day', order='DESC')    # 以创建日期字段 day为单位 倒序 查询
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_NUM_BLOG)  # 每 settings.EACH_PAGE_NUM_BLOG 多少篇进行分页
    page_num = request.GET.get('page', 1)  # 获取页码参数
    page_of_blogs = paginator.get_page(page_num)
    current_page = page_of_blogs.number  # 获取当前页
    blogs = page_of_blogs.object_list
    blog_types = BlogType.objects.all()
    page_range = list(range(max(current_page - 2, 1), current_page)) \
                 + list(range(current_page, min(current_page + 2, paginator.num_pages) + 1))  # 获取页码范围
    # 显示省略号
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 显示第一页和最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 分类项统计数量 方法一 先写入内存，对服务器资源消耗大
    '''
    blog_type_list = []
    for blog_type in blog_types:
        # 为blog_type类添加一个blog_count属性
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_type_list.append(blog_type)
    '''
    # 分类项统计数量 方法二，只有查询才写入内存
    blog_type_list  = BlogType.objects.annotate(blog_count=Count('blog'))

    # 归档日期数量统计数量
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month,
                                         created_time__day=blog_date.day).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs', 'blog_types', 'blog_dates', 'paginator', 'page_of_blogs', 'page_range'] \
        = blogs, blog_type_list, blog_dates_dict, paginator, page_of_blogs, page_range
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = blog_common_data(request, blogs_all_list)
    blogs, blog_types, blog_dates, paginator, page_of_blogs, page_range = \
        context['blogs', 'blog_types', 'blog_dates', 'paginator', 'page_of_blogs', 'page_range']

    return render(request, 'blog/blog_list.html',
                  {'blogs': blogs, 'blog_types': blog_types,'paginator': paginator,
                   'page_of_blogs': page_of_blogs, 'page_range': page_range, 'blog_dates': blog_dates})

def blogs_with_type(request, blog_with_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_with_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)

    context = blog_common_data(request, blogs_all_list)
    blogs, blog_types, blog_dates, paginator, page_of_blogs, page_range = \
        context['blogs', 'blog_types', 'blog_dates', 'paginator', 'page_of_blogs', 'page_range']

    return render(request, 'blog/blogs_with_type.html',
                  {'blogs': blogs, 'blog_types': blog_types, 'paginator': paginator, 'blog_dates': blog_dates,
                   'blog_type': blog_type, 'page_of_blogs': page_of_blogs, 'page_range': page_range})

def blogs_with_date(request, year, month, day):
    blogs_all_list = Blog.objects.filter(created_time__year=year,
                                         created_time__month=month,
                                         created_time__day=day)
    blogs_with_date = '{}年{}月{}日'.format(year, month, day)

    context = blog_common_data(request, blogs_all_list)
    blogs, blog_types, blog_dates, paginator, page_of_blogs, page_range = \
        context['blogs', 'blog_types', 'blog_dates', 'paginator', 'page_of_blogs', 'page_range']

    return render(request, 'blog/blogs_with_date.html',
                  {'blogs': blogs, 'blog_types': blog_types, 'paginator': paginator, 'blog_dates': blog_dates,
                   'page_of_blogs': page_of_blogs, 'page_range': page_range, 'blogs_with_date': blogs_with_date})

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_count_once(request, blog)
    blog_content_type = ContentType.objects.get_for_model(blog)

    blog_previous = Blog.objects.filter(created_time__gt=blog.created_time).last()
    blog_next = Blog.objects.filter(created_time__lt=blog.created_time).first()

    '''
    优化到 comment/templatetags/comment_tags.py 中的方法中，此处去掉
    comment_form = CommentForm(initial={'content_type': blog_content_type.model,
                                    'object_id': blog_pk, 'reply_comment_id': 0})
    comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None).order_by('-comment_time')
    comment_count = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk).count() 
    '''

    response = render(request, 'blog/blog_detail.html',
                             {'blog': blog, 'blog_previous': blog_previous,
                              'blog_next': blog_next})
    response.set_cookie(read_cookie_key, 'true')
    return response
