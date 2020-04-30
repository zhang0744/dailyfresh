from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse  # 反向解析
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from user.models import User, Address
from django.views.generic import View  # 类视图
from itsdangerous import TimedJSONWebSignatureSerializer as lizer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_active_email
from utils.mixin import LoginRequiredMixin
import re


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
            return redirect(reverse('user:login'))  # 跳转到首页


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

# user/login


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
        return render(request, 'login.html', {'username': username, 'checked': checked})

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

                # 获取要跳转到的地址,如果为空跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))
                # 重定向跳转到next_url
                response = redirect(next_url)

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
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

# user/logout


class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        # 清楚session
        logout(request)

        # 跳转到首页
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    '''用户中心-信息页'''

    def get(self, request):
        '''显示页面'''
        return render(request, 'user_center_info.html', {'page': 'user'})

# /user/order


class UserOrderView(LoginRequiredMixin, View):
    '''用户中心-订单页'''

    def get(self, request):
        '''显示页面'''
        return render(request, 'user_center_order.html', {'page': 'order'})

# /user/site


class UserSiteView(LoginRequiredMixin, View):
    '''用户中心-地址页'''

    def get(self, request):
        '''显示页面'''
        user = request.user  # 获取user信息

        try:
            address = Address.objects.get(user=user, is_default=True)
        except:
            # 没有默认地址
            address = None

        errmsg = request.GET.get('errmsg', '')

        return render(request, 'user_center_site.html', {'page': 'site', 'adderss': adderss, 'errmsg': errmsg})

    def post(self, request):
        '''添加地址处理'''
        # 接受数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据完整性
        if not all([receiver, addr, phone]):
            # 接受数据不完整 重定向页面并传入错误参数
            return redirect(reverse(user: site) + "?errmsg='数据不完整'")

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            # 手机号格式化不正确 重定向页面并传入错误参数
            return redirect(reverse(user: site) + "?errmsg='手机号不正确'")

        # 业务处理 保存数据
        # 如果已经有默认收货地址,添加地址is_default为false
        user = request.user  # 获取user信息

        try:
            address = Address.objects.get(user=user, is_default=True)
        except:
            # 没有默认地址
            address = None
        if address:
            is_default = True
        else:
            is_default = False
        # 添加地址
        Address.objects.create(user=user, receiver=receiver, addr=addr, zip_code=zip_code, phone=phone, is_default=is_default)

        # 返回应答,刷新页面
        return redirect(reverse('user:site'))
