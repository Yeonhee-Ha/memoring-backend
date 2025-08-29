from rest_framework import serializers
from .models import RecallQuestion, RecallAnswer

class RecallQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecallQuestion
        fields = ["id", "text", "answer_key", "difficulty", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

class RecallAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecallAnswer
        fields = ["id", "question", "answer_text", "is_correct", "response_time_sec", "created_at"]
        read_only_fields = ["id", "is_correct", "created_at"]
