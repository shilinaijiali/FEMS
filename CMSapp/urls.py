from django.urls import path
from CMSapp.views import views_consumable, views_common, views_admin

app_name = 'CMSapp'

urlpatterns = [
    # 公共方法
    # 通过任意外键获取耗材
    path('get_sn_list_by_all_type/', views_common.get_sn_list_by_all_type.as_view(), name='get_sn_list_by_all_type'),
    # 多条件获取耗材
    path('get_sn_list_by_mul_condition/', views_common.get_sn_list_by_mul_condition.as_view(), name='get_sn_list_by_mul_condition'),
    # 通过耗材类型获取所有所属类别
    path('get_all_type_by_ConsumableType/', views_common.get_all_type_by_ConsumableType.as_view(), name='get_all_type_by_ConsumableType'),
    # 通过耗材类型获取相应耗材
    path('get_ConsumableList_by_ConsumableType/', views_common.get_ConsumableList_by_ConsumableType.as_view(), name='get_ConsumableList_by_ConsumableType'),
    path('get_ConsumableList_by_Other/', views_common.get_ConsumableList_by_Other.as_view(), name='get_ConsumableList_by_Other'),
    path('get_all_consumable_list/', views_common.get_all_consumable_list.as_view(), name='get_all_consumable_list'),

    # 耗材查询
    path('ConsumableQuery/', views_consumable.ConsumableQuery.as_view(), name='ConsumableQuery'),
    # 耗材使用，添加使用记录
    # 网板
    path('ScreenUsage/', views_consumable.ScreenUsage.as_view(), name='ScreenUsage'),
    path('ScreenUsageInfo/', views_consumable.ScreenUsageInfo.as_view(), name='ScreenUsageInfo'),
    path('ScreenCheck/', views_consumable.ScreenCheck.as_view(), name='ScreenCheck'),
    # 刀模
    path('MouldsUsage/', views_consumable.MoudlsUsage.as_view(), name='MouldsUsage'),
    path('MouldsUsageInfo/', views_consumable.MouldsUsageInfo.as_view(), name='MouldsUsageInfo'),
    # 耗材的库存操作，领取和归还
    path('StockOperation/', views_consumable.StockOperation.as_view(), name='StockOperation'),
    path('StockInfo/', views_consumable.StockInfo.as_view(), name='StockInfo'),
    # 确认报废
    path('ConfirmScrap/', views_consumable.ConfirmScrap.as_view(), name='ConfirmScrap'),
    path('get_C_Scrap_list/', views_consumable.get_C_Scrap_list.as_view(), name='get_C_Scrap_list'),
    # 强制报废
    path('ForcedScrap/', views_consumable.ForcedScrap.as_view(), name='ForcedScrap'),
    path('ScrapInfo/', views_consumable.ScrapInfo.as_view(), name='ScrapInfo'),
    # 下载excel文档耗材模板
    path('export_excel/', views_consumable.export_excel.as_view(), name='export_excel'),
    # 上传excel文档新增耗材
    path('create_consumable_by_excel/', views_consumable.create_consumable_by_excel.as_view(), name='create_consumable_by_excel'),
    # admin 添加Consumable时选择耗材类型时过滤其他选项
    path('get_version_list/', views_admin.get_version_list, name='get_version_list'),
    path('get_tooltype_list/', views_admin.get_tooltype_list, name='get_tooltype_list'),
    path('get_model_list/', views_admin.get_model_list, name='get_model_list'),
]
