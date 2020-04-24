from django.conf.urls import url
from user.views import RegisterView, ActiveView, LoginView
urlpatterns = [
    # url(r'^a$', views.a),
    # url(r'^register$', views.register, name='register'), #注册
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册视图类
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 激活处理
    url(r'^login$', LoginView.as_view(), name='login'),  # 登录
]
