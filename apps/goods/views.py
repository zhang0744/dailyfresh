from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache
# Create your views here.

'''首页'''


class IndexView(View):
    '''显示首页'''

    def get(self, request):
        # 尝试获取缓存数据
        context = cache.get('index_page_data')
        if context is None:
            '''没有缓存,生成缓存'''
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

            # 要缓存的数据
            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners}

            # 设置缓存
            cache.set('index_page_data', context, 3600)

        # 获取购物车信息
        cart_count = 0
        user = request.user
        if user.is_authenticated():  # 判断用户是否登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 添加数据到缓存数据
        context.update(cart_count=cart_count)

        # 渲染模板
        return render(request, 'index.html', context)
