# TODO: split up into abstract API implementations

import coreapi
import coreschema
from . import serializers, filters, models, forms, permissions
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from django import shortcuts
from django.conf import settings
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_auth.registration.views import SocialLoginView
from rest_framework import views, viewsets, schemas, response, mixins, decorators, renderers, permissions as drf_permissions

schema_view = get_schema_view(
  openapi.Info(
    title='FAIRshake API v2',
    default_version='v2',
    description='A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability',
    terms_of_service='https://fairshake.cloud/',
    contact=openapi.Contact(
      email='avi.maayan@mssm.edu',
    ),
    license=openapi.License(name='Apache 2.0 License'),
  ),
  validators=['flex', 'ssv'],
  public=True,
  permission_classes=[drf_permissions.AllowAny],
)

class GithubLogin(SocialLoginView):
  adapter_class = GitHubOAuth2Adapter

class OrcidLogin(SocialLoginView):
  adapter_class = OrcidOAuth2Adapter

class CustomTemplateHTMLRenderer(renderers.TemplateHTMLRenderer):
  def get_template_context(self, data, renderer_context):
    context = super(CustomTemplateHTMLRenderer, self).get_template_context(data, renderer_context) or {}
    view = renderer_context['view']
    request = view.request
    return view.get_template_context(request, context)

class CustomModelViewSet(viewsets.ModelViewSet):
  renderer_classes = [
    renderers.JSONRenderer,
    CustomTemplateHTMLRenderer,
    renderers.BrowsableAPIRenderer,
  ]
  permission_classes = [
    permissions.IdentifiablePermissions,
  ]

  def get_model(self):
    return self.model
  
  def get_model_name(self):
    return self.get_model()._meta.verbose_name_raw
  
  def get_form(self):
    return self.form

  def save_form(self, request, form):
    instance = form.save()
    instance.authors.add(request.user)
    return instance

  def get_queryset(self):
    return getattr(self, 'queryset', self.get_model().objects.all())

  def get_template_names(self):
    return ['fairshake/generic/page.html']
  
  def get_detail_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    item = self.get_object()
    form_cls = self.get_form()
    form = form_cls(instance=item)

    return {
      'model': self.get_model_name(),
      'action': self.action,
      'item': item,
      'form': form,
      'children': {
        child: paginator_cls(
          child_queryset,
          page_size,
        ).get_page(
          request.GET.get('page')
        )
        for child, child_queryset in item.children().items()
      },
    }
  
  def get_list_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    form_cls = self.get_form()
    form = form_cls(request.GET)

    return {
      'model': self.get_model_name(),
      'action': self.action,
      'form': form,
      'items': paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    }

  def get_template_context(self, request, context):
    return dict(context,
      **self.get_detail_template_context(
        request, context
      ) if self.detail else self.get_list_template_context(
        request, context
      ),
    )

  @decorators.action(
    detail=False, methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def add(self, request, pk=None):
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST)
    instance = self.save_form(request, form)
    return shortcuts.redirect(
      self.get_model_name()+'-detail',
      pk=instance.id,
    )

  @decorators.action(
    detail=True,
    methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def modify(self, request, pk=None):
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST, instance=shortcuts.get_object_or_404(self.get_model(), id=pk))
    instance = self.save_form(request, form)
    return shortcuts.redirect(
      self.get_model_name()+'-detail',
      pk=pk,
    )

  @decorators.action(
    detail=True,
    methods=['get'],
  )
  def delete(self, request, pk=None):
    item = shortcuts.get_object_or_404(self.get_model(), pk=pk)
    item.delete()
    return shortcuts.redirect(
      self.get_model_name()+'-list'
    )

class DigitalObjectViewSet(CustomModelViewSet):
  model = models.DigitalObject
  form = forms.DigitalObjectForm
  serializer_class = serializers.DigitalObjectSerializer
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(CustomModelViewSet):
  model = models.Metric
  form = forms.MetricForm
  serializer_class = serializers.MetricSerializer
  filter_class = filters.MetricFilterSet

class ProjectViewSet(CustomModelViewSet):
  model = models.Project
  form = forms.ProjectForm
  serializer_class = serializers.ProjectSerializer
  filter_class = filters.ProjectFilterSet

class RubricViewSet(CustomModelViewSet):
  model = models.Rubric
  form = forms.RubricForm
  serializer_class = serializers.RubricSerializer
  filter_class = filters.RubricFilterSet

class AssessmentViewSet(CustomModelViewSet):
  model = models.Assessment
  form = forms.AssessmentForm
  serializer_class = serializers.AssessmentSerializer
  filter_classes = filters.AssessmentFilterSet
  permission_classes = [
    permissions.AssessmentPermissions,
  ]

  def get_queryset(self):
    if self.request.user.is_anonymous:
      return models.Assessment.objects.none()
    return models.Assessment.objects.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(assessor=self.request.user)
    )

  def save_form(self, request, form):
    instance = form.save(commit=False)
    instance.assessor = request.user
    instance.save()
    return instance

class AssessmentRequestViewSet(CustomModelViewSet):
  model = models.AssessmentRequest
  form = forms.AssessmentRequestForm
  queryset = models.AssessmentRequest.objects.all()
  serializer_class = serializers.AssessmentRequestSerializer
  filter_classes = filters.AssessmentRequestFilterSet
  permission_classes = [
    permissions.AssessmentRequestPermissions,
  ]

  def save_form(self, request, form):
    instance = form.save(commit=False)
    instance.requestor = request.user
    instance.save()
    return instance
  
class ScoreViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
  ):
  ''' Request an score for a digital resource
  '''
  queryset = models.Assessment.objects.all()
  serializer_class = serializers.AssessmentSerializer
  filter_class = filters.ScoreFilterSet
  pagination_class = None

  def list(self, request):
    '''
    Generate aggregate scores on a per-rubric and per-metric basis.
    '''
    scores = {}
    metrics = {}

    for assessment in self.filter_queryset(self.get_queryset()):
      if scores.get(assessment.rubric.id) is None:
        scores[assessment.rubric.id] = {}
      for answer in models.Answer.objects.filter(
        assessment=assessment.id,
      ):
        if metrics.get(answer.metric.id) is None:
          metrics[answer.metric.id] = answer.metric.title
        if scores[assessment.rubric.id].get(answer.metric.id) is None:
          scores[assessment.rubric.id][answer.metric.id] = []
        scores[assessment.rubric.id][answer.metric.id].append(answer.value())

    return response.Response({
      'scores': {
        rubric: {
          metric: sum(value)/len(value)
          for metric, value in score.items()
        }
        for rubric, score in scores.items()
      },
      'metrics': metrics,
    })
