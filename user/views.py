import string
import random
import time

from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail

from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile

def login_modal_form(request):
    login_form = LoginForm(request.POST)
    data = {}

    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def login(request):
    # username = request.POST.get('username', '')
    # password = request.POST.get('password', '')
    # user = auth.authenticate(request, username=username, password=password)
    # referer = request.META.get('HTTP_REFERER', reverse('home'))
    # if user is not None:
    #     auth.login(request, user)
    #     return  redirect(referer)
    # else:
    #     return render(request, 'error.html', {'message': '用户名或密码错误！'})
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()
    return render(request, 'user/login.html', {'login_form': login_form})

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            # 创建用户 第一种方法
            user = User.objects.create_user(username, email, password)
            user.save()
            del request.session['register_code'] # 用户保存到数据库后，清除浏览器session验证码数据
            '''
            创建用户 第二种方法
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            user.save()
            '''
            # 登陆用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()
    return render(request, 'user/register.html', {'reg_form': reg_form})

def loginout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)

def change_nickname(request,):
    redirect_to = request.GET.get('form', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user) # 提取数据
        if form.is_valid(): # 验证数据是否为空和是否登录
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)

def bind_email(request):
    redirect_to = request.GET.get('form', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request) # 提取数据
        if form.is_valid(): # 验证数据是否为空和是否登录
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()
    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now_time = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now_time - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now_time
            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码: %s' % code,
                'lly1103@aliyun.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)    # 密码修改后退出登录，让用户用新密码重新登录
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    return render(request, 'form.html',
                    {'page_title': '修改密码', 'form_title': '修改密码',
                    'submit_text': '修改', 'form': form, 'return_back_url': redirect_to})


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)  # 提取数据
        if form.is_valid():  # 验证数据是否为空和是否登录
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清除session
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'user/forgot_password.html', context)