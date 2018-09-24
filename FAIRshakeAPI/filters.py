import django_filters as filters
import logging
from . import models, search

class AllInFilter(filters.AllValuesFilter, filters.BaseInFilter):
  pass

class IdentifiableFilterSet(filters.FilterSet):
  id = AllInFilter()
  authors = AllInFilter()
  q = filters.CharFilter(field_name='id', method='filter_query')
  url = filters.CharFilter(field_name='url', lookup_expr='icontains')

  def get_search_vector(self):
    return self.__class__.Meta.search_vector

  def filter_query(self, qs, name, q):
    return self.get_search_vector()(qs).query(q)

  class Meta:
    abstract = True

class DigitalObjectFilterSet(IdentifiableFilterSet):
  class Meta:
    model = models.DigitalObject
    search_vector = search.DigitalObjectSearchVector
    fields = '__all__'

class MetricFilterSet(IdentifiableFilterSet):
  class Meta:
    model = models.Metric
    search_vector = search.MetricSearchVector
    fields = '__all__'

class ProjectFilterSet(IdentifiableFilterSet):
  class Meta:
    model = models.Project
    search_vector = search.ProjectSearchVector
    fields = '__all__'

class RubricFilterSet(IdentifiableFilterSet):
  class Meta:
    model = models.Rubric
    search_vector = search.RubricSearchVector
    fields = '__all__'


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

class AssessmentRequestFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.AssessmentRequest
    fields = '__all__'

class AuthorFilterSet(filters.FilterSet):
  id = AllInFilter()
  class Meta:
    model = models.Author
    fields = '__all__'

class ScoreFilterSet(filters.FilterSet):
  id = AllInFilter()

  digital_object = filters.BaseInFilter(field_name='target')
  url = filters.CharFilter(field_name='target__url', lookup_expr='icontains')
  metric = filters.BaseInFilter(field_name='rubric__metrics')

  class Meta:
    model = models.Assessment
    exclude = ('timestamp',)
