from rest_framework import serializers
from . import models

class IdentifiableModelMixinSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.IdentifiableModelMixin
    fields = '__all__'
    abstract = True

class DigitalObjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.DigitalObject
    fields = '__all__'

class ProjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Project
    fields = '__all__'

class MetricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Metric
    fields = '__all__'

class RubricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Rubric
    fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Assessment
    fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Answer
    fields = '__all__'

class ScoreSerializer(serializers.BaseSerializer):
  def to_representation(self, obj):
    return obj.score()

class DigitalObjectsToRubricsSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.DigitalObject
    fields = ('rubrics',)
