from rest_framework import serializers
from .models import Assessment, AssessmentResult

class AssessmentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentResult
        fields = ('question', 'answer',)

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ('obj', 'rubric', 'type', 'answers',)
        read_only_fields = ('timestamp',)

    answers = AssessmentResultSerializer(many=True)
