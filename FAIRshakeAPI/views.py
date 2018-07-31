# TODO: split up into abstract API implementations

import coreapi
import coreschema
from rest_framework import views, viewsets, permissions, schemas, response, mixins, decorators
from rest_auth.registration.views import SocialLoginView
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from . import serializers, filters, models
from .permissions import IsAuthorOrReadOnly

class CustomOpenAPIRenderer(OpenAPIRenderer):
  def get_customizations(self):
    return dict(super().get_customizations(),
      info={
        'description': 'A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability',
        'contact': {
          'x-role': 'responsible organization',
          'email': 'avi.maayan@mssm.edu',
        },
        'version': '1.0.1',
      },
      tags=[
        {"name": "NIHdatacommons"},
        {"name": "Maayanlab"},
      ],
    )

@decorators.api_view()
@decorators.renderer_classes([SwaggerUIRenderer, CustomOpenAPIRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='FAIRshake API')
    return response.Response(generator.get_schema(request=request))

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

class AnswerViewSet(viewsets.ModelViewSet):
  queryset = models.Answer.objects.all()
  serializer_class = serializers.AnswerSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.AnswerFilterSet

class AssessmentViewSet(viewsets.ModelViewSet):
  queryset = models.Assessment.objects.all()
  serializer_class = serializers.AssessmentSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.AssessmentFilterSet

class DigitalObjectViewSet(viewsets.ModelViewSet):
  queryset = models.DigitalObject.objects.all()
  serializer_class = serializers.DigitalObjectSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(viewsets.ModelViewSet):
  queryset = models.Metric.objects.all()
  serializer_class = serializers.MetricSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.MetricFilterSet

class ProjectViewSet(viewsets.ModelViewSet):
  queryset = models.Project.objects.all()
  serializer_class = serializers.ProjectSerializer
  permission_classes = (
    permissions.IsAuthenticatedOrReadOnly,
    IsAuthorOrReadOnly,
  )
  filter_class = filters.ProjectFilterSet

class RubricViewSet(viewsets.ModelViewSet):
  queryset = models.Rubric.objects.all()
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

    for assessment in self.filter_queryset(self.get_queryset()):
      if scores.get(assessment.rubric.id) is None:
        scores[assessment.rubric.id] = {}
      for answer in models.Answer.objects.filter(
        assessment=assessment.id,
      ):
        if scores[assessment.rubric.id].get(answer.metric.id) is None:
          scores[assessment.rubric.id][answer.metric.id] = []
        scores[assessment.rubric.id][answer.metric.id].append(answer.value())

    return response.Response({
      rubric: {
        metric: sum(value)/len(value)
        for metric, value in score.items()
      }
      for rubric, score in scores.items()
    })
