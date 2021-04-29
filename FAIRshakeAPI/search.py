from django.db.models import Case, When, Value, FloatField
from django.db.models.functions import Replace, Length
from FAIRshakeAPI import models
from functools import reduce

class SearchVector:
  def __init__(self, qs=None):
    self.queryset = qs or self.get_model().objects.filter(id__isnull=False)

  def get_model(self):
    return self.model
  
  def get_filters(self):
    return getattr(self, 'filters', [])

  def get_queryset(self):
    return self.queryset

  def query(self, q):
    return self.get_queryset().annotate(
      rank=reduce(
        lambda F, f, q=q: (F+f(q)) if F is not None else f(q),
        self.get_filters(),
        None,
      )
    ).filter(rank__gt=0).order_by('-rank', *self.get_model()._meta.ordering).distinct()


def icontains_overlap(field, query):
  return Case(
    When(**{
      "{field}__icontains".format(field=field): query
    }, then=Value(len(query))),
    default=Value(0),
    output_field=FloatField(),
  )

def istartswith_overlap(field, query):
  return Case(
    When(**{
      "{field}__istartswith".format(field=field): query
    }, then=Value(len(query))),
    default=Value(0),
    output_field=FloatField(),
  )

def url_similarity(field, query):
  ''' Assign a value to the similarity
  the length of the url - the length of our query taken out of that url
  '''
  norm_field = Replace(
    Replace(field, Value('http://'), Value('https://')),
    Value('https://www.'), Value('https://')
  )
  norm_query = Value(query.replace('http://', 'https://').replace('https://www.', 'https://'))
  return Length(norm_field, output_field=FloatField()) - Length(Replace(norm_field, norm_query, Value('')), output_field=FloatField())

class IdentifiableSearchVector(SearchVector):
  filters = [
    lambda q: icontains_overlap('title', q) * 5.0,
    lambda q: url_similarity('url', q) * 10.0,
    lambda q: icontains_overlap('description', q),
    lambda q: icontains_overlap('tags', q),
    lambda q: istartswith_overlap('authors__first_name', q),
    lambda q: istartswith_overlap('authors__last_name', q),
    lambda q: istartswith_overlap('authors__email', q),
  ]

class ProjectSearchVector(IdentifiableSearchVector):
  model = models.Project

class DigitalObjectSearchVector(IdentifiableSearchVector):
  model = models.DigitalObject

class RubricSearchVector(IdentifiableSearchVector):
  model = models.Rubric

class MetricSearchVector(IdentifiableSearchVector):
  model = models.Metric
