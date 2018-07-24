from rest_framework import serializers
from . import models

class IdentifiableModelMixinSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
    user = self.context.get('request').user
    validated_data.update(
      authors=[
        user.id,
      ],
    )
    return super(IdentifiableModelMixinSerializer, self).create(validated_data)
  
  def update(self, instance, validated_data):
    user = self.context.get('request').user
    validated_data.update(
      authors=list(set(validated_data.get('authors', [])+[user.id])),
    )
    return super(IdentifiableModelMixinSerializer, self).update(instance, validated_data)

  class Meta:
    abstract = True

class DigitalObjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.DigitalObject
    fields = '__all__'
    read_only_fields = (
      'authors',
    )

class ProjectSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Project
    exclude = (
      'digital_objects',
    )
    read_only_fields = (
      'authors',
    )

class MetricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Metric
    fields = '__all__'
    read_only_fields = (
      'authors',
    )

class RubricSerializer(IdentifiableModelMixinSerializer):
  class Meta:
    model = models.Rubric
    fields = '__all__'
    read_only_fields = (
      'authors',
    )

class AssessmentSerializer(serializers.ModelSerializer):
  assessor = serializers.PrimaryKeyRelatedField(
    read_only=True,
    default=serializers.CurrentUserDefault(),
  )

  class Meta:
    model = models.Assessment
    fields = '__all__'
    read_only_fields = (
      'requestor',
      'assessor',
      'timestamp',
    )

class AnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Answer
    fields = '__all__'

class ScoreSerializer(serializers.BaseSerializer):
  def to_representation(self, obj):
    return {
      'id': obj.id,
      'score': obj.score(),
    }

class DigitalObjectsToRubricsSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.DigitalObject
    fields = ('id', 'rubrics',)
