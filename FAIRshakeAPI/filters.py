import django_filters as filters
from . import models

class AllInFilter(filters.AllValuesFilter, filters.BaseInFilter):
  pass

class AnswerFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Answer
    fields = '__all__'

class AssessmentFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Assessment
    fields = '__all__'

class AuthorFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Author
    fields = '__all__'

class DigitalObjectFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.DigitalObject
    fields = '__all__'

class MetricFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Metric
    fields = '__all__'

class ProjectFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Project
    fields = '__all__'

class RubricFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Rubric
    fields = '__all__'

class ScoreFilterSet(filters.FilterSet):
  id = AllInFilter()

  digital_object = filters.BaseInFilter(field_name='target')
  url = filters.CharFilter(field_name='target__url', lookup_expr='icontains')
  metric = filters.BaseInFilter(field_name='rubric__metrics')

  class Meta:
    model = models.Assessment
    exclude = ('timestamp',)
