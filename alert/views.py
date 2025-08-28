from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Alert
from .serializers import AlertCreateUpdateSerializer, AlertReadSerializer
from .services import send_alert

# Create your views here.

class AlertViewSet(viewsets.ModelViewSet):
  permission_classes = [permissions.IsAuthenticated]

  def get_queryset(self):
    return Alert.objects.filter(user=self.request.user)
  
  def get_serializer_class(self):
    if self.action in ["list", "retrieve", "pending"]:
      return AlertReadSerializer
    return AlertCreateUpdateSerializer
  
  def perform_create(self, serializer):
    serializer.save(user=self.request.user)

  # due 알림 목록 (서버 잡/크론이 주기 호출)
  def pending(self, request):
    # GET /alert/pending/?until=5 # 지금부터 5분 이내 PENDING
    minutes = int(request.query_params.get("until", 5))
    now = timezone.now()
    until = now + timezone.timedelta(minutes = minutes)
    qs = Alert.objects.Filter(
      user = request.user,
      status=Alert.Status.PENDING,
      send_at__lte = until
    ).order_by("send_at")
    return Response(AlertReadSerializer(qs, many=True).data)

  # 개별 전송 트리거
  @action(detail=True, methods=["post"])
  def send_due(self, request):
    minutes = int(request.query_params.get("until", 5))
    now = timezone.now()
    until = now + timezone.timedelta(minutes=minutes)
    qs = Alert.objects.filter(user=request.user, status=Alert.Status.PENDING, send_at__lte=until).order_by ("send_at")
    
    results = []
    for a in qs:
      results.append(AlertReadSerializer(send_alert(a)).data)
    return Response(results,status = status.HTTP_200_OK)
  
  

