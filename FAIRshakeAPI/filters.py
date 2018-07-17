import django_filters as filters
from .models import (
  Answer,
  Assessment,
  Author,
  DigitalObject,
  Metric,
  Project,
  Rubric,
)

class AnswerFilterSet(filters.FilterSet):
  class Meta:
    model = Answer
    fields = '__all__'

class AssessmentFilterSet(filters.FilterSet):
  class Meta:
    model = Assessment
    fields = '__all__'

class AuthorFilterSet(filters.FilterSet):
  class Meta:
    model = Author
    fields = '__all__'

class DigitalObjectFilterSet(filters.FilterSet):
  class Meta:
    model = DigitalObject
    fields = '__all__'

class MetricFilterSet(filters.FilterSet):
  class Meta:
    model = Metric
    fields = '__all__'

class ProjectFilterSet(filters.FilterSet):
  class Meta:
    model = Project
    fields = '__all__'

class RubricFilterSet(filters.FilterSet):
  class Meta:
    model = Rubric
    fields = '__all__'
