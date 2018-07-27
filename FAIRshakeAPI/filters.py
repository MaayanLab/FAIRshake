import django_filters as filters
from . import models

class AnswerFilterSet(filters.FilterSet):
  class Meta:
    model = models.Answer
    fields = '__all__'

class AssessmentFilterSet(filters.FilterSet):
  class Meta:
    model = models.Assessment
    fields = '__all__'

class AuthorFilterSet(filters.FilterSet):
  class Meta:
    model = models.Author
    fields = '__all__'

class DigitalObjectFilterSet(filters.FilterSet):
  class Meta:
    model = models.DigitalObject
    fields = '__all__'

class MetricFilterSet(filters.FilterSet):
  class Meta:
    model = models.Metric
    fields = '__all__'

class ProjectFilterSet(filters.FilterSet):
  class Meta:
    model = models.Project
    fields = '__all__'

class RubricFilterSet(filters.FilterSet):
  class Meta:
    model = models.Rubric
    fields = '__all__'

class ScoreFilterSet(filters.FilterSet):
  class Meta:
    model = models.Assessment
    exclude = ('timestamp',)
