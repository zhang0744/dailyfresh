"""
Django settings for dailyfresh project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))  # 设置搜索目录

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'oa#j@pm=la3_5o6y4ht!*2s1$bxjd(sju!cq!0tjv^^i7cmy=t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*', ]


# Application definition
# 注册应用
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',  # 用户模块
    'cart',  # 购物车模块
    'goods',  # 商品模块
    'order',  # 订单模块
    'tinymce',  # 富文本编辑器
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dailyfresh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 设置模板路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dailyfresh.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
# 设置数据库信息
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dailyfresh',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    }
}

# Django认证系统使用的模型类
AUTH_USER_MODEL = 'user.User'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'  # 设置语言

TIME_ZONE = 'Asia/Shanghai'  # 设置时区

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static'
# STATIC_ROOT = os.path.join(BASE_DIR,'static/')  # 实际环境中静态文件目录设置
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # 设置静态文件目录

# 富文本编辑器配置
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',  # 设置主题/功能为高级
    'width': 600,
    'height': 400,
}


# 邮件发送设置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# 发送邮件的SMTP服务器地址
EMAIL_HOST = 'smtp.163.com'
# 发送邮件的SMTP服务器端口号
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'zhanghao_7811@163.com'
# 授权码
EMAIL_HOST_PASSWORD = 'ISMRELHWWCQONFGT'
# 发件人设置
EMAIL_FROM = '天天生鲜<zhanghao_7811@163.com>'


# Django连接redis配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": "密码",
        },
    },
}
# 设置session存在缓存里面
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = 'default'
# REDIS_TIMEOUT=7*24*60*60
# CUBES_REDIS_TIMEOUT=60*60
# NEVER_REDIS_TIMEOUT=365*24*60*60


# 设置使用fdfs文件系统
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDFSStorage'

# 指定login页面地址
LOGIN_URL = '/user/login'

# 设置fdfs使用的client.conf文件的路径
FDFS_CLIENT_CONF = '/etc/fdfs/client.conf'
# 设置fdfs使用的nginx服务ip与端口
FDFS_URL = 'http://10.32.9.63/'
