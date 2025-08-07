from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login, logout

from .models import *
from .serializers import *

@method_decorator(csrf_exempt, name='dispatch')
class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSignupSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email = email, password = password)

        if user is not None:
            login(request, user)
            return Response({"message":"로그인 성공"}, status = 200)
        return Response({"error": "이메일 또는 비밀번호가 틀렸습니다."}, status = 400)
    
    

#CSRF 보호 임시로 끄기
@method_decorator(csrf_exempt, name='dispatch')
class UserLogoutView(APIView):
    #permission_classes = [permissions.IsAuthenticated]
    def post(self,request):
        logout(request)
        return Response({"message" : "로그아웃 성공"}, status = 200)
    


@method_decorator(csrf_exempt, name='dispatch')
class UserMeView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)