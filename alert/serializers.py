from rest_framework import serializers
from django.utils import timezone
from .models import Alert

class AlertCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["id", "title", "body", "channel", "send_at", "schedule_id", "metadata"]
        read_only_fields = ["id"]

    def validate_send_at(self, value):
        # 과거 예약 방지(1분 대기)
        if value < timezone.now() - timezone.timedelta(minutes=1):
            raise serializers.ValidationError("send_at은 현재 시각 이후여야 합니다.")
        return value

class AlertReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            "id", "title", "body", "channel",
            "send_at", "delivered_at", "status", "retries", "last_error",
            "schedule_id", "metadata", "created_at", "updated_at"
        ]
        read_only_fields = fields
