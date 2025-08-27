from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorialViewSet,SettingViewSet

router = DefaultRouter()
router.register("", TutorialViewSet, basename="tutorial")
router.register(r"setting", SettingViewSet, basename="setting")

urlpatterns = [
    path("", include(router.urls)),
]
