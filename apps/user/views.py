from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse  # 反向解析
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from user.models import User
from django.views.generic import View  # 类视图
from itsdangerous import TimedJSONWebSignatureSerializer as lizer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_active_email
import re


def a(request):
    return render(request, 'a.html')
# Create your views here.


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''打开注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''处理注册请求'''
        # 注册
        if request.method == 'GET':
            return render(request, 'register.html')
        elif request.method == 'POST':
            # 接受数据
            username = request.POST.get('user_name')
            password = request.POST.get('pwd')
            email = request.POST.get('email')
            allow = request.POST.get('allow')
            # 进行数据校验
            if not all([username, password, email]):
                return render(request, 'register.html', {'errmsg': '数据不完整'})
            # 邮箱检验
            if not re.match(r'^[a-z0-9][\w.-]*@[a-z0-9-]+(\.[a-z]{2,5}){1,2}$', email):
                return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
            #  协议校验
            if allow != 'on':
                return render(request, 'register.html', {'errmsg': '请同意协议'})

            # 校验用户名是否重复
            try:
                is_user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 用户不存在
                is_user = None
            if is_user:
                # 用户名已存在
                return render(request, 'register.html', {'errmsg': '用户名已存在'})

            # 进行注册业务处理
            user = User.objects.create_user(username, email, password)  # 创建用户
            user.is_active = 0  # 设置未激活
            user.save()

            # 生成token
            slizer = lizer(settings.SECRET_KEY, 3600)
            info = {'user_id': user.id}
            token = slizer.dumps(info)
            token = token.decode('utf8')  # 解码

            # 发送激活邮件
            send_active_email.delay(email, username, token)

            # 返回应答
            return redirect(reverse('goods:index'))  # 跳转到首页


class ActiveView(View):
    '''邮箱激活处理'''

    def get(self, request, token):
        slizer = lizer(settings.SECRET_KEY, 3600)
        try:
            info = slizer.loads(token)
            # 获取用户id
            user_id = info['user_id']
            # 获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))

        except SignatureExpired as e:
            return HttpResponse('激活链接过期')


class LoginView(View):
    '''登录'''

    def get(self, request):
        '''显示登录页面'''
         # 判断是否记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 打开模板
        return render(request, 'login.html', {'username':username, 'checked':checked})

    def post(self, request):
        '''登录校验'''
        # 接受数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # print('username:%s,password:%s' % (username, passwoed))
        # 校验数据的完整性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户登录状态
                login(request, user)
                
                # 跳转到首页
                response = redirect(reverse('goods:index'))
                
                # 判断是否需要记住用户名
                remember = request.POST.get('remember')
                
                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


def register(request):
    # 注册
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 邮箱检验
        if not re.match(r'^[a-z0-9][\w.-]*@[a-z0-9-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        #  协议校验
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            is_user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户不存在
            is_user = None
        if is_user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行注册业务处理
        user = User().objects.create_user(username, email, password)  # 创建用户
        user.is_active = 0  # 设置未激活
        user.save()

        # 返回应答
        return redirect(reverse('goods:index'))  # 跳转到首页
