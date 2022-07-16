from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_access_list'

router = NetBoxRouter()
router.register('access-lists', views.AccessListViewSet)
router.register('standard-acl-rules', views.AccessListStandardRuleViewSet)
router.register('extended-acl-rules', views.AccessListExtendedRuleViewSet)

urlpatterns = router.urls
