from rest_framework import serializers
from .models import (
  Answer,
  Assessment,
  Author,
  DigitalObject,
  IdentifiableModelMixin,
  Metric,
  Project,
  Rubric,
  Score,
)

class IdentifiableModelMixinSerializer(serializers.ModelSerializer):
  class Meta:
    model = IdentifiableModelMixin
    fields = '__all__'
    abstract = True

class AuthorSerializer(serializers.ModelSerializer):
  class Meta:
    model = Author
    fields = '__all__'

class DigitalObjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = DigitalObject
    fields = '__all__'

class ProjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = Project
    fields = '__all__'

class MetricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = Metric
    fields = '__all__'

class RubricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = Rubric
    fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Assessment
    fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Answer
    fields = '__all__'

class ScoreSerializer(serializers.ModelSerializer):
  class Meta:
    model = Score
    fields = ['score']
