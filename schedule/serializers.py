from rest_framework import serializers
from .models import Schedule, ScheduleStep

class ScheduleStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleStep
        fields = ["id", "step_number", "voice_url", "transcript", "parsed_value", "created_at"]

class ScheduleSerializer(serializers.ModelSerializer):
    steps = ScheduleStepSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id", "user", "parsed_title", "parsed_date",
            "parsed_time", "parsed_ampm", "processed", "created_at", "steps"
        ]
