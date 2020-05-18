from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

import os
import django
from django.template import loader, RequestContext
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# 创建实例对象
app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/1')

# 定义任务函数


@app.task
def send_active_email(email, username, token):
    '''发送激活邮件'''
    subject = '天天生鲜'  # 邮件题目
    message = ''  # 邮件内容
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [email]  # 收件人列表
    # html格式邮件内容
    html_message = '<h1>%s, 欢迎成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://10.32.9.63:80/user/active/%s">10.32.9.63:80/user/active/%s</a>' % (username, token, token)
    # 发送邮件
    send_mail(subject, message, sender, receiver, html_message=html_message)


@app.task
def generate_static_index_html():
    '''生成首页静态页面'''
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播图信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类展示信息
    for type in types:
        # 获取商品种类对应的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取商品种类对应的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，
        type.title_banners = title_banners
        type.image_banners = image_banners

    # 设置模板传入参数
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners,
               }

    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')
    # 2.渲染模板
    static_index_html = temp.render(context)

    # 生成首页静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:  # 打开文件
        f.write(static_index_html)  # 写入文件
