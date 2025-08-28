from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet
from . import views
#from views import * 

app_name = "alert" 

router = DefaultRouter()
router.register("", AlertViewSet, basename="alert")

urlpatterns = [
  path("", include(router.urls)),
]