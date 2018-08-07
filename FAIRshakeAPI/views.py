# TODO: split up into abstract API implementations

import coreapi
import coreschema
from . import serializers, filters, models
from .permissions import IsAuthorOrReadOnly
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from django.db.models import Q
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_auth.registration.views import SocialLoginView
from rest_framework import views, viewsets, permissions, schemas, response, mixins, decorators, renderers

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
  permission_classes=(permissions.AllowAny,),
)

class GithubLogin(SocialLoginView):
  adapter_class = GitHubOAuth2Adapter

class OrcidLogin(SocialLoginView):
  adapter_class = OrcidOAuth2Adapter

class RequestAssessmentViewSet(viewsets.ViewSet):
  ''' Request an assessment for a digital resource
  '''
  queryset = models.DigitalObject.objects.all()
  schema = schemas.AutoSchema(manual_fields=[
    coreapi.Field(
      'rubric',
      required=False,
      description='Specific rubric to use for the assessment, default will be internal associations',
      location='query',
      schema=coreschema.String(),
    ),
    coreapi.Field(
      'methodology',
      required=False,
      description='Type of assessment requested, default is FAIRshake manual assessment',
      location='query',
      schema=coreschema.String(),
    ),
    coreapi.Field(
      'callback',
      required=False,
      description='Where to send the results when they are ready, default is FAIRshake itself',
      location='query',
    ),
  ])

  def retrieve(self, request, pk=None, format=None):
    # TODO: perform assessment
    return response.Response({})

class CustomTemplateHTMLRenderer(renderers.TemplateHTMLRenderer):
  def get_template_context(self, data, renderer_context):
    context = super(CustomTemplateHTMLRenderer, self).get_template_context(data, renderer_context)
    view = renderer_context['view']

    context['model'] = view.get_model()._meta.model_name

    paginator_cls = view.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']

    if view.action == 'retrieve':
      item = view.get_object()
      context['item'] = item
      context['children'] = {
        child: paginator_cls(
          child_queryset,
          page_size,
        ).get_page(
          view.request.GET.get('page')
        )
        for child, child_queryset in item.children().items()
      }

    elif view.action == 'list':
      context['items'] = paginator_cls(
        view.filter_queryset(
          view.get_queryset()
        ),
        page_size,
      ).get_page(
        view.request.GET.get('page')
      )

    return context

class CustomModelViewSet(viewsets.ModelViewSet):
  renderer_classes = [
    renderers.JSONRenderer,
    CustomTemplateHTMLRenderer,
    renderers.BrowsableAPIRenderer,
  ]
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )

  def get_model(self):
    return self.model

  def get_queryset(self):
    return getattr(self, 'queryset', self.get_model().objects.all())

  def get_template_names(self):
    return ['fairshake/' + self.get_model()._meta.model_name + '/' + self.action + '.html']

class DigitalObjectViewSet(CustomModelViewSet):
  model = models.DigitalObject
  serializer_class = serializers.DigitalObjectSerializer
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(CustomModelViewSet):
  model = models.Metric
  serializer_class = serializers.MetricSerializer
  filter_class = filters.MetricFilterSet

class ProjectViewSet(CustomModelViewSet):
  model = models.Project
  serializer_class = serializers.ProjectSerializer
  filter_class = filters.ProjectFilterSet

class RubricViewSet(CustomModelViewSet):
  model = models.Rubric
  serializer_class = serializers.RubricSerializer
  filter_class = filters.RubricFilterSet

class AssessmentViewSet(CustomModelViewSet):
  model = models.Assessment

  def get_queryset(self):
    if self.request.user.is_anonymous:
      return models.Assessment.objects.none()
    return models.Assessment.objects.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(requestor=self.request.user)
      | Q(assessor=self.request.user)
    )

  serializer_class = serializers.AssessmentSerializer
  filter_classes = filters.AssessmentFilterSet
  permission_classes = (
    permissions.IsAuthenticated,
  )

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
