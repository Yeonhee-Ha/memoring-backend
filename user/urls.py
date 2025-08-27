from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # 기본 로그인 (access/refresh 발급)
    TokenRefreshView,      # refresh → access 재발급
    TokenVerifyView        # 토큰 유효성 검증
)
from .views import UserViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    # UserViewSet 라우터
    path("", include(router.urls)),

    # JWT 기본 제공 엔드포인트
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
