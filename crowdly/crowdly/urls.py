"""crowdly URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework.authtoken.views import ObtainAuthToken
from django.conf.urls.static import static
from django.conf import settings

from api import DeviceViewSet, LocationViewSet, ManageLocationViewSet, DeviceHistoryViewSet, LocationHistoryViewSet, \
    ChangeDeviceViewSet, DeviceStateHistoryViewSet

from views import HomeView, DeviceList, DeviceDetail

router = routers.DefaultRouter()
router.register(r'devices', DeviceViewSet, "Device")
router.register(r'setpp', ChangeDeviceViewSet, "ChangeDevice")
router.register(r'locations', LocationViewSet, "Location")
router.register(r'manage', ManageLocationViewSet, base_name='manage')
router.register(r'devicehistory', DeviceHistoryViewSet, 'DeviceHistory')
router.register(r'locationhistory', LocationHistoryViewSet, 'LocationHistory')
router.register(r'statehistory', DeviceStateHistoryViewSet, base_name='statehistory')



urlpatterns = [
    # url(r'^admin/', admin.site.urls),

    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/', include(router.urls)),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^auth-token/', ObtainAuthToken.as_view()),

    url(r'^device/$', DeviceList.as_view(), name='device-list-view'),
    url(r'^device/(?P<slug>[\w-]+)/$', DeviceDetail.as_view(), name='device-detail-view'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


