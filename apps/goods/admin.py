from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType, IndexPromotionBanner, IndexGoodsBanner, IndexTypeGoodsBanner
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    # 新增或更新表操作
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 执行生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的数据缓存
        cache.delete('index_page_data')

    # 删除表数据操作
    def delete_model(self, request, obj):
        super().delete_model(request, obj)

        # 执行生成静态页面
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的数据缓存
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
