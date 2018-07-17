from rest_framework import viewsets, permissions

from .serializers import (
  AnswerSerializer,
  AssessmentSerializer,
  AuthorSerializer,
  DigitalObjectSerializer,
  MetricSerializer,
  ProjectSerializer,
  RubricSerializer,
)
from .filters import (
  AnswerFilterSet,
  AssessmentFilterSet,
  AuthorFilterSet,
  DigitalObjectFilterSet,
  MetricFilterSet,
  ProjectFilterSet,
  RubricFilterSet,
)
from .models import (
  Answer,
  Assessment,
  Author,
  DigitalObject,
  Metric,
  Project,
  Rubric,
)

class AnswerViewSet(viewsets.ModelViewSet):
  queryset = Answer.objects.all()
  serializer_class = AnswerSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = AnswerFilterSet

class AssessmentViewSet(viewsets.ModelViewSet):
  queryset = Assessment.objects.all()
  serializer_class = AssessmentSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = AssessmentFilterSet

class AuthorViewSet(viewsets.ModelViewSet):
  queryset = Author.objects.all()
  serializer_class = AuthorSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = AuthorFilterSet

class DigitalObjectViewSet(viewsets.ModelViewSet):
  queryset = DigitalObject.objects.all()
  serializer_class = DigitalObjectSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = DigitalObjectFilterSet

class MetricViewSet(viewsets.ModelViewSet):
  queryset = Metric.objects.all()
  serializer_class = MetricSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = MetricFilterSet

class ProjectViewSet(viewsets.ModelViewSet):
  queryset = Project.objects.all()
  serializer_class = ProjectSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = ProjectFilterSet

class RubricViewSet(viewsets.ModelViewSet):
  queryset = Rubric.objects.all()
  serializer_class = RubricSerializer
  permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
  filter_class = RubricFilterSet
