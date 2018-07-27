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

    read_only_fields = (
      'id',
      'authors',
    )

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

class AnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Answer
    fields = '__all__'
    read_only_fields = (
      'id',
      'assessment',
    )

class AssessmentSerializer(serializers.ModelSerializer):
  project = serializers.PrimaryKeyRelatedField(queryset=models.Project.objects.all())
  target = serializers.PrimaryKeyRelatedField(queryset=models.DigitalObject.objects.all())
  rubric = serializers.PrimaryKeyRelatedField(queryset=models.Rubric.objects.all())

  answers = AnswerSerializer(many=True)

  def create(self, validated_data):
    user = self.context.get('request').user
    answers_data = validated_data.pop('answers')
    assessment = models.Assessment.objects.create(**validated_data, assessor=user)
    for answer_data in answers_data:
      models.Answer.objects.create(assessment=assessment, **answer_data)
    return assessment

  class Meta:
    model = models.Assessment
    fields = '__all__'
    read_only_fields = (
      'id',
      'requestor',
      'assessor',
      'timestamp',
    )
    depth = 1

class AnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Answer
    fields = '__all__'
    read_only_fields = (
      'id',
      'assessment',
    )
