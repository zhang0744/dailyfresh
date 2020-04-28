from django.core.mail import send_mail
from django.conf import settings
from celery import Celery

import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

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
	html_message = '<h1>%s, 欢迎成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://10.32.9.63:80/user/active/%s">10.32.9.63:80/user/active/%s</a>'%(username, token, token)
	# 发送邮件
	send_mail(subject, message, sender, receiver, html_message=html_message)