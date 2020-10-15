from ajax_select import register, LookupChannel
from FAIRshakeAPI import models
from django.template.loader import render_to_string
from django.db.models import Q

class IdentifiableLookupChannel(LookupChannel):
  def check_auth(self, request):
    return True

  def get_query(self, q, request):
    return self.model.objects.filter(title__icontains=q).order_by('title')

  def format_item_display(self, item):
    return render_to_string(
      'fairshake/generic/element-offset.html',
      dict(
        model=self.model._meta.verbose_name_raw,
        item=item,
      ),
    )

class EmbeddedIdentifiableLookupChannel(IdentifiableLookupChannel):
  def format_item_display(self, item):
    return render_to_string(
      'fairshake/generic/element-offset.html',
      dict(
        model=self.model._meta.verbose_name_raw,
        item=item,
        embedded=True,
      ),
    )

@register('digital_objects-embedded')
class DigitalObjectLookup(EmbeddedIdentifiableLookupChannel):
  model = models.DigitalObject

@register('projects-embedded')
class ProjectLookup(EmbeddedIdentifiableLookupChannel):
  model = models.Project

@register('rubrics-embedded')
class RubricLookup(EmbeddedIdentifiableLookupChannel):
  model = models.Rubric

@register('metrics-embedded')
class MetricLookup(EmbeddedIdentifiableLookupChannel):
  model = models.Metric


@register('digital_objects')
class DigitalObjectLookup(IdentifiableLookupChannel):
  model = models.DigitalObject

@register('projects')
class ProjectLookup(IdentifiableLookupChannel):
  model = models.Project

@register('rubrics')
class RubricLookup(IdentifiableLookupChannel):
  model = models.Rubric

@register('metrics')
class MetricLookup(IdentifiableLookupChannel):
  model = models.Metric

@register('authors')
class AuthorLookup(LookupChannel):
  def check_auth(self, request):
    return True

  def get_query(self, q, request):
    return models.Author.objects.filter(
      Q(username__icontains=q)
      | Q(email__icontains=q)
      | Q(first_name__icontains=q)
      | Q(last_name__icontains=q)
    ).order_by('id')

  def format_item_display(self, item):
    return item.username + ((' <'+item.email+'>') if item.email else '')
