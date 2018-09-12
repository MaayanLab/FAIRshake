# TODO: split up into abstract API implementations

from . import serializers, filters, models, forms, search
from .permissions import ModelDefinedPermissions
from django import shortcuts, forms as django_forms
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.forms import ModelChoiceField
from rest_framework import views, viewsets, schemas, response, mixins, decorators, renderers, permissions

def callback_or_redirect(request, *args, **kwargs):
  callback = request.GET.get('callback', None)
  if callback is None:
    return shortcuts.redirect(
      *args,
      **kwargs,
    )
  else:
    return shortcuts.redirect(callback)

def get_or_create(model, **kwargs):
  try:
    return model.objects.current.get(**kwargs)
  except:
    return model.objects.create(**kwargs)

class CustomTemplateHTMLRenderer(renderers.TemplateHTMLRenderer):
  def get_template_context(self, data, renderer_context):
    context = super().get_template_context(data, renderer_context) or {}
    view = renderer_context['view']
    request = view.request
    return view.get_template_context(request, context)

class CustomModelViewSet(viewsets.ModelViewSet):
  renderer_classes = [
    renderers.JSONRenderer,
    CustomTemplateHTMLRenderer,
    renderers.BrowsableAPIRenderer,
  ]
  permission_classes = [ModelDefinedPermissions,]

  def get_model(self):
    return self.model
  
  def get_model_name(self):
    return self.get_model()._meta.verbose_name_raw

  def get_queryset(self):
    qs = getattr(self, 'queryset', None)
    return self.get_model().objects.current.all() if qs is None else qs
  
  def filter_queryset(self, qs):
    ''' Ensure all resulting filter sets are distinct '''
    return super().filter_queryset(qs).order_by(*self.get_model()._meta.ordering).distinct()

  def get_template_names(self):
    return ['fairshake/generic/page.html']

  def get_template_context(self, request, context):
    return getattr(
      self,
      'get_%s_template_context' % (self.action),
      getattr(
        self,
        'get_%s_template_context' % ('detail' if self.detail else 'list'),
        lambda request, context: context
      )
    )(
      request,
      dict(
        context,
        model=self.get_model_name(),
        action=self.action,
      ),
    )

class IdentifiableModelViewSet(CustomModelViewSet):
  lookup_field = 'slug'

  def get_form(self):
    return self.form

  def get_model_children(self, obj):
    for child in self.get_model().MetaEx.children:
      child_attr = getattr(obj, child)
      yield (child_attr.model._meta.verbose_name_raw, child_attr.current.all())

  def save_form(self, request, form):
    instance = form.save()
    instance.authors.add(request.user)
    return instance

  @decorators.action(
    detail=False, methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def add(self, request, slug=None, **kwargs):
    self.check_permissions(request)
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST)
    instance = self.save_form(request, form)
    return callback_or_redirect(request,
      self.get_model_name()+'-detail',
      slug=instance.slug,
    )

  @decorators.action(
    detail=True,
    methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def modify(self, request, slug=None):
    item = self.get_object()
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST, instance=item)
    instance = self.save_form(request, form)
    return callback_or_redirect(request,
      self.get_model_name()+'-detail',
      slug=instance.slug,
    )

  @decorators.action(
    detail=True,
    methods=['get'],
  )
  def remove(self, request, slug=None):
    item = self.get_object()
    self.check_object_permissions(request, item)
    item.delete()
    return callback_or_redirect(request,
      self.get_model_name()+'-list'
    )

  def get_add_template_context(self, request, context):
    form_cls = self.get_form()
    form = form_cls(request.GET)

    return dict(context, **{
      'form': form,
    })

  def get_modify_template_context(self, request, context):
    item = self.get_object()
    form_cls = self.get_form()
    form = form_cls(instance=item)

    return dict(context, **{
      'item': item,
      'form': form,
    })

  def get_retrieve_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    item = self.get_object()

    return dict(context, **{
      'item': item,
      'children': {
        child: paginator_cls(
          child_attr,
          page_size,
        ).get_page(
          request.GET.get('page')
        )
        for child, child_attr in self.get_model_children(item)
      },
    })

  def get_list_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    form_cls = self.get_form()
    form = form_cls(request.GET)

    return dict(context, **{
      'form': form,
      'items': paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    })

class DigitalObjectViewSet(IdentifiableModelViewSet):
  model = models.DigitalObject
  form = forms.DigitalObjectForm
  serializer_class = serializers.DigitalObjectSerializer
  filter_class = filters.DigitalObjectFilterSet

class MetricViewSet(IdentifiableModelViewSet):
  model = models.Metric
  form = forms.MetricForm
  serializer_class = serializers.MetricSerializer
  filter_class = filters.MetricFilterSet

class ProjectViewSet(IdentifiableModelViewSet):
  model = models.Project
  form = forms.ProjectForm
  serializer_class = serializers.ProjectSerializer
  filter_class = filters.ProjectFilterSet
  
  @decorators.action(
    detail=True,
    methods=['get'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def stats(self, request, slug=None):
    item = self.get_object()
    self.check_object_permissions(request, item)
    return response.Response()
  
  def get_stats_template_context(self, request, context):
    item = self.get_object()
    return dict(context, **{
      'item': self.get_object(),
      'plots': [
        'TablePlot',
        'RubricPieChart',
        'RubricsInProjectsOverlay',
        'DigitalObjectBarBreakdown',
      ]
    })

class RubricViewSet(IdentifiableModelViewSet):
  model = models.Rubric
  form = forms.RubricForm
  serializer_class = serializers.RubricSerializer
  filter_class = filters.RubricFilterSet

class AssessmentViewSet(CustomModelViewSet):
  model = models.Assessment
  serializer_class = serializers.AssessmentSerializer
  filter_classes = filters.AssessmentFilterSet

  def get_queryset(self):
    if self.request.user.is_anonymous:
      return models.Assessment.objects.none()
    return models.Assessment.objects.current.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(assessor=self.request.user)
    )
  
  def get_objects(self, request):
    target_id = request.GET.get('target', None)
    rubric_id = request.GET.get('rubric', None)
    project_id = request.GET.get('project', None)

    if target_id is None or rubric_id is None:
      pass # TODO redirect to prepare

    if project_id:
      assessment = get_or_create(models.Assessment,
        project=models.project.objects.get(id=project_id),
        target=models.target.objects.get(id=target_id),
        rubric=models.rubric.objects.get(id=rubric_id),
        assessor=request.user,
        methodology='user',
      )
    else:
      assessment = get_or_create(models.Assessment,
        target=models.target.objects.get(id=target_id),
        rubric=models.rubric.objects.get(id=rubric_id),
        assessor=request.user,
        methodology='user',
      )

    answers = []
    for metric in assessment.rubric.metrics.current.all():
      answer = get_or_create(models.Answer,
        assessment=assessment,
        metric=metric,
      )
      answer_form = forms.AnswerForm(
        dict(request.GET, **request.POST),
        instance=answer,
        prefix=answer.metric.id,
      )
      answers.append({
        'form': answer_form,
        'instance': answer,
      })

    return {
      'assessment': assessment,
      'answers': answers,
    }

  def save_form(self, request, form):
    item = self.get_objects(request)
    for answer in item.answers:
      answer['form'].save()

    cache.delete_many([
      ','.join(map('='.join, request.GET.items())),
      *map('='.join, request.GET.items()),
    ])

  @decorators.action(
    detail=False, methods=['get'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def perform(self, request, **kwargs):
    self.check_permissions(request)

  @decorators.action(
    detail=False, methods=['get'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def prepare(self, request, **kwargs):
    self.check_permissions(request)

  def get_detail_template_context(self, request, context):
    item = self.get_objects(request)
    return dict(context, **item)

  def get_list_template_context(self, request, context):
    # List rubric objects
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']

    return dict(context, **{
      'items': paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    })

  def get_prepare_template_context(self, request, context):
    if target is not None:
      targets = models.DigitalObject.objects.filter(id=target)
    else:
      targets = search.DigitalObjectSearchVector().query(q)

    if rubric is not None:
      rubrics = models.Rubric.objects.filter(id=target)
    else:
      rubrics = None
      if target is not None:
        rubrics = targets.first().rubrics.current.all()
      if rubrics is None or not rubrics.exists():
        rubrics = models.Rubric.objects.current.all()
      if rubrics.count() == 1:
        rubric = rubrics.first().id

    if project is not None:
      projects = models.Project.objects.filter(id=project)
    else:
      projects = None
      if target is not None:
        projects = targets.first().projects.current.all()
      if projects is None or projects.exists():
        projects = models.Project.objects.current.all()
      if projects.count() == 1:
        project = projects.first().id

    if project is not None:
      assessment_form = forms.AssessmentForm(dict(request.GET, **{
        'target': targets.first().id,
        'rubric': rubrics.first().id,
        'project': projects.first().id,
      }))
    else:
      assessment_form = forms.AssessmentForm(dict(request.GET, **{
        'target': targets.first().id,
        'rubric': rubrics.first().id,
      }))

class AssessmentRequestViewSet(CustomModelViewSet):
  model = models.AssessmentRequest
  form = forms.AssessmentRequestForm
  queryset = models.AssessmentRequest.objects.all()
  serializer_class = serializers.AssessmentRequestSerializer
  filter_classes = filters.AssessmentRequestFilterSet

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
  queryset = models.Assessment.objects.current.all()
  serializer_class = serializers.AssessmentSerializer
  filter_class = filters.ScoreFilterSet
  pagination_class = None

  def list(self, request):
    '''
    Generate aggregate scores on a per-rubric and per-metric basis.
    '''
    key = ','.join(map('='.join,request.GET.items()))
    result = cache.get(key)

    if result is None:
      scores = {}
      metrics = {}

      for assessment in self.filter_queryset(self.get_queryset()):
        if scores.get(assessment.rubric.id) is None:
          scores[assessment.rubric.id] = {}
        for answer in assessment.answers.all():
          if metrics.get(answer.metric.id) is None:
            metrics[answer.metric.id] = answer.metric.title
          if scores[assessment.rubric.id].get(answer.metric.id) is None:
            scores[assessment.rubric.id][answer.metric.id] = []
          scores[assessment.rubric.id][answer.metric.id].append(answer.value())

      result = {
        'scores': {
          rubric: {
            metric: sum(value)/len(value)
            for metric, value in score.items()
          }
          for rubric, score in scores.items()
        },
        'metrics': metrics,
      }
      cache.set(key, result, 60 * 60)

    return response.Response(result)

  @decorators.action(
    detail=False, methods=['get'],
  )
  def hist(self, request):
    '''
    Generate histogram of answers
    '''
    key = 'hist-'+','.join(map('='.join,request.GET.items()))
    answers = cache.get(key)

    if answers is None:
      answers = {}
      for assessment in self.filter_queryset(self.get_queryset()):
        for answer in assessment.answers.current.all():
          value = answer.value()
          answers[value] = answers.get(value, 0) + 1
      cache.set(key, answers, 60 * 60)
      
    return response.Response(answers)
