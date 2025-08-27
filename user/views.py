from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .serializers import UserSerializer, UserSignupSerializer


class UserViewSet(viewsets.ViewSet):
    """
    회원가입 / 로그인(JWT 발급) / 로그아웃(토큰 블랙리스트) / 내정보 조회/수정
    """

    # 회원가입 + JWT 발급
    @action(detail=False, methods=["post"], url_path="signup")
    def signup(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 회원가입 후 JWT 발급
            refresh = RefreshToken.for_user(user)
            response_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 로그인 (JWT 발급)
    @action(detail=False, methods=["post"], url_path="login")
    def login_user(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error": "이메일 또는 비밀번호가 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃 (refresh token 블랙리스트 처리)
    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[permissions.IsAuthenticated])
    def logout_user(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh 토큰이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃 성공"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "유효하지 않은 토큰"}, status=status.HTTP_400_BAD_REQUEST)

    # 내 정보 조회
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="me")
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    # 내 정보 수정
    @action(detail=False, methods=["patch"], permission_classes=[permissions.IsAuthenticated], url_path="me")
    def update_me(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
