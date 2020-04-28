from django.conf.urls import url
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView
urlpatterns = [
    # url(r'^a$', views.a),
    # url(r'^register$', views.register, name='register'), #注册
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册视图类
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 激活处理
    url(r'^login$', LoginView.as_view(), name='login'),  # 登录

    url(r'^$', UserInfoView.as_view(), name='user'),  # 用户中心-信息页
    url(r'^order$', UserInfoView.as_view(), name='order'),  # 用户中心-订单页
    url(r'^site$', UserInfoView.as_view(), name='site'),  # 用户中心-地址页
]
