from rest_framework import serializers
from .models import Rubric, QuestionGroup, Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('index', 'question', 'value_type')

class QuestionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionGroup
        fields = ('index', 'name', 'description', 'questions')

    questions = QuestionSerializer(many=True)

class RubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubric
        fields = ('name', 'description', 'question_groups')

    question_groups = QuestionGroupSerializer(many=True)
