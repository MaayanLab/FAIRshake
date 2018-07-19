# TODO: split up into abstract API implementations

import coreapi
import coreschema
from rest_framework import views, viewsets, permissions, schemas, response
from . import serializers, filters, models

class RequestAssessmentViewSet(viewsets.ViewSet):
  ''' Request an assessment for a digital resource
  '''
  queryset = models.DigitalObject.objects.all()
  schema = schemas.AutoSchema(manual_fields=[
    coreapi.Field(
      'rubric',
      required=False,
      description='Specific rubric to use for the assessment, default will be internal associations',
      location='query',
      schema=coreschema.String(),
    ),
    coreapi.Field(
      'methodology',
      required=False,
      description='Type of assessment requested, default is FAIRshake manual assessment',
      location='query',
      schema=coreschema.String(),
    ),
    coreapi.Field(
      'callback',
      required=False,
      description='Where to send the results when they are ready, default is FAIRshake itself',
      location='query',
    ),
  ])

  def retrieve(self, request, pk=None, format=None):
    # TODO: perform assessment
    return response.Response({})

class AnswerViewSet(viewsets.ModelViewSet):
  queryset = models.Answer.objects.all()
  serializer_class = serializers.AnswerSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.AnswerFilterSet

class AssessmentViewSet(viewsets.ModelViewSet):
  queryset = models.Assessment.objects.all()
  serializer_class = serializers.AssessmentSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.AssessmentFilterSet

class AuthorViewSet(viewsets.ModelViewSet):
  queryset = models.Author.objects.all()
  serializer_class = serializers.AuthorSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.AuthorFilterSet

class DigitalObjectViewSet(viewsets.ModelViewSet):
  queryset = models.DigitalObject.objects.all()
  serializer_class = serializers.DigitalObjectSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(viewsets.ModelViewSet):
  queryset = models.Metric.objects.all()
  serializer_class = serializers.MetricSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.MetricFilterSet

class ProjectViewSet(viewsets.ModelViewSet):
  queryset = models.Project.objects.all()
  serializer_class = serializers.ProjectSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.ProjectFilterSet

class RubricViewSet(viewsets.ModelViewSet):
  queryset = models.Rubric.objects.all()
  serializer_class = serializers.RubricSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = filters.RubricFilterSet

class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = models.Score.objects.all()
  serializer_class = serializers.ScoreSerializer
  filter_class = filters.ScoreFilterSet

class DigitalObjectsToRubricsViewSet(viewsets.ModelViewSet):
  queryset = models.DigitalObject.objects.all()
  serializer_class = serializers.DigitalObjectsToRubricsSerializer
  filter_class = filters.DigitalObjectsToRubricsFilterSet
