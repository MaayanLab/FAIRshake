import django_filters as filters
import logging
from . import models, search

class IdentifiableFilterSet(filters.FilterSet):
  authors = filters.ModelMultipleChoiceFilter(queryset=models.Author.objects.all())
  q = filters.CharFilter(field_name='id', method='filter_query')
  url = filters.CharFilter(field_name='url', lookup_expr='url_similar')
  url_strict = filters.CharFilter(field_name='url', lookup_expr='url_strict')

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
  class Meta:
    model = models.Answer
    fields = '__all__'

class AssessmentFilterSet(filters.FilterSet):
  class Meta:
    model = models.Assessment
    fields = '__all__'

class AssessmentRequestFilterSet(filters.FilterSet):
  class Meta:
    model = models.AssessmentRequest
    fields = '__all__'

class AuthorFilterSet(filters.FilterSet):
  class Meta:
    model = models.Author
    fields = '__all__'

class ScoreFilterSet(filters.FilterSet):
  digital_object = filters.ModelChoiceFilter(queryset=models.DigitalObject.objects.filter(id__isnull=False), field_name='target')
  url = filters.CharFilter(field_name='target__url', lookup_expr='url_similar')
  url_strict = filters.CharFilter(field_name='target__url', lookup_expr='url_strict')
  metric = filters.ModelChoiceFilter(queryset=models.Metric.objects.filter(id__isnull=False), field_name='rubric__metrics')

  class Meta:
    model = models.Assessment
    exclude = ('timestamp',)
