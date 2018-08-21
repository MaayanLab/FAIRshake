from django.db.models import Q
from FAIRshakeAPI import models
from functools import reduce

class SearchVector:
  def __init__(self, qs=None):
    self.queryset = qs or self.get_model().objects.all()

  def get_model(self):
    return self.model
  
  def get_filters(self):
    return getattr(self, 'filters', [])

  def get_queryset(self):
    return self.queryset

  def query(self, q):
    return self.get_queryset().filter(
      reduce(
        lambda F, f, q=q: (F|f(q)) if F is not None else f(q),
        self.get_filters(),
        None,
      )
    )

def safe_id(q):
  try:
    return Q(id=int(q))
  except:
    return Q()

class IdentifiableSearchVector(SearchVector):
  filters = [
    safe_id,
    lambda q: Q(title__icontains=q),
    lambda q: Q(url__icontains=q),
    lambda q: Q(description__icontains=q),
    lambda q: Q(tags__icontains=q),
    lambda q: Q(type__icontains=q),
    lambda q: Q(authors__first_name__icontains=q),
  ]

class ProjectSearchVector(IdentifiableSearchVector):
  model = models.Project

class DigitalObjectSearchVector(IdentifiableSearchVector):
  model = models.DigitalObject

class RubricSearchVector(IdentifiableSearchVector):
  model = models.Rubric

class MetricSearchVector(IdentifiableSearchVector):
  model = models.Metric
