from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

#class HelloView(APIView):

    #@swagger_auto_schema(
    #    operation_description="GET 요청 예시입니다.",
    #    responses={200: openapi.Response('성공')},
    #)
#    def get(self, request):
#        return Response({"message": "Hello, world!"})
