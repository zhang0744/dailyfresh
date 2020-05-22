from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.http import HttpResponse
from goods.models import GoodsType, GoodsSKU, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner
from django_redis import get_redis_connection
from django.core.cache import cache
from order.models import OrderGoods
# Create your views here.


class IndexView(View):
    '''首页'''

    def get(self, request):
        '''显示首页'''
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


class DetailView(View):  # /goods/商品id
    '''详情页'''

    def get(self, request, goods_id):
        '''显示详情页'''
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在, 跳转到首页
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取前两个新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('create_time')[:2]

        # 获取同一个spu的商品的信息
        same_spu_skus = GoodsSKU.objects.filter(goodsSPU=sku.goodsSPU).exclude(id=goods_id)

        # 获取购物车信息
        cart_count = 0
        user = request.user
        if user.is_authenticated():  # 判断用户是否登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的用户历史浏览记录
            # conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存5条最新信息
            conn.ltrim(history_key, 0, 4)

        # 组织模板参数
        context = {'sku': sku, 'types': types,
                   'sku_orders': sku_orders,
                   'new_skus': new_skus,
                   'same_spu_skus': same_spu_skus,
                   'cart_count': cart_count}

        return render(request, 'detail.html', context)
