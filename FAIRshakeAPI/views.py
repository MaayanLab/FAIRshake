# TODO: split up into abstract API implementations

import coreapi
import coreschema
from rest_framework import views, viewsets, permissions, schemas, response, mixins, decorators, renderers
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from . import serializers, filters, models
from .permissions import IsAuthorOrReadOnly
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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
    return dict(context,
      context=context,
      # Pass the actual filtered queryset--beyond simply the serialization
      #  so we have access to the models themselves.
      queryset=view.filter_queryset(view.get_queryset()),
    )

class CustomModelViewSet(viewsets.ModelViewSet):
  renderer_classes = [
    CustomTemplateHTMLRenderer,
    renderers.BrowsableAPIRenderer,
    renderers.JSONRenderer,
  ]

  def get_model(self):
    return self.model

  def get_queryset(self):
    return getattr(self, 'queryset', self.get_model().objects.all())

  def get_template_names(self):
    return ['fairshake/' + self.get_model()._meta.model_name + '/' + self.action + '.html']

class AnswerViewSet(CustomModelViewSet):
  model = models.Answer
  serializer_class = serializers.AnswerSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.AnswerFilterSet

class AssessmentViewSet(CustomModelViewSet):
  model = models.Assessment
  serializer_class = serializers.AssessmentSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.AssessmentFilterSet

class DigitalObjectViewSet(CustomModelViewSet):
  model = models.DigitalObject
  serializer_class = serializers.DigitalObjectSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(CustomModelViewSet):
  model = models.Metric
  serializer_class = serializers.MetricSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.MetricFilterSet

class ProjectViewSet(CustomModelViewSet):
  model = models.Project
  serializer_class = serializers.ProjectSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.ProjectFilterSet

class RubricViewSet(CustomModelViewSet):
  model = models.Rubric
  serializer_class = serializers.RubricSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.RubricFilterSet

class ScoreViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
  ''' Request an score for a digital resource
  '''
  queryset = models.Assessment.objects.all()
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
