from ajax_select import register, LookupChannel
from FAIRshakeAPI import models
from django.template.loader import render_to_string

class IdentifiableLookupChannel(LookupChannel):
  def get_query(self, q, request):
    return self.model.objects.filter(title__icontains=q).order_by('title')

  def format_item_display(self, item):
    return render_to_string(
      'fairshake/generic/element.html',
      dict(
        model=self.model._meta.verbose_name_raw,
        item=item,
      ),
    )

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
