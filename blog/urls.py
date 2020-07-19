from django.urls import path

from blog import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    # http:localhost:80000/blog/1/
    path('<int:blog_pk>/', views.blog_detail, name='blog_detail'),
    path('type/<int:blog_with_pk>/', views.blogs_with_type, name='blogs_with_type'),
    path('date/<int:year>/<int:month>/<int:day>/', views.blogs_with_date, name='blogs_with_date'),
]