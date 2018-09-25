# TODO: split up into abstract API implementations

import json
from . import serializers, filters, models, forms, search
from .permissions import ModelDefinedPermissions
from .assessments import Assessment
from django import shortcuts, forms as django_forms
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.forms import ModelChoiceField
from django.urls import reverse
from rest_framework import views, viewsets, schemas, response, mixins, decorators, renderers, permissions
from functools import reduce

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
    return model.objects.get(**kwargs)
  except:
    return model.objects.create(**kwargs)

def redirect_with_params(request, *args, **kwargs):
  return shortcuts.redirect(
    reverse(*args, **kwargs) + '?' + '&'.join(map('='.join, request.GET.items()))
  )

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
  permission_classes = [ModelDefinedPermissions,]

  def get_model(self):
    return self.model
  
  def get_model_name(self):
    return self.get_model()._meta.verbose_name_raw
  
  def get_queryset(self):
    return getattr(self, 'queryset', self.get_model().objects.all())
  
  def filter_queryset(self, qs):
    ''' Ensure all resulting filter sets are distinct '''
    return super().filter_queryset(qs).order_by(*self.get_model()._meta.ordering).distinct()

  def get_template_names(self):
    return ['fairshake/generic/page.html']

  def get_template_context(self, request, context):
    return dict(context,
      model=self.get_model_name(),
      action=self.action,
      **getattr(self, 'get_%s_template_context' % (self.action),
        getattr(self, 'get_%s_template_context' % ('detail' if self.detail else 'list'),
          lambda request, context: context
        )
      )(request, context),
    )

class IdentifiableModelViewSet(CustomModelViewSet):
  def get_model_children(self, obj):
    for child in self.get_model().MetaEx.children:
      child_attr = getattr(obj, child)
      yield (child_attr.model._meta.verbose_name_raw, child_attr.all())

  def get_form(self):
    form_cls = self.form
    if self.detail and self.request.method == 'GET':
      form = form_cls(instance=self.get_object())
    elif self.request.method == 'GET':
      form = form_cls(initial=dict(self.request.GET.dict(), **{
        'authors': [self.request.user],
      }))
    elif self.request.method == 'POST' and self.detail:
      form = form_cls(self.request.POST, instance=self.get_object())
    elif self.request.method == 'POST':
      form = form_cls(self.request.POST)
    else:
      form = None
    return form

  def save_form(self, request, form):
    if form.is_valid():
      instance = form.save()
      return instance

  @decorators.action(
    detail=False, methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def add(self, request, pk=None, **kwargs):
    self.check_permissions(request)
    if request.method == 'GET':
      return response.Response()
    form = self.get_form()
    instance = self.save_form(request, form)
    if instance:
      return callback_or_redirect(request,
        self.get_model_name()+'-detail',
        pk=instance.id,
      )
    return response.Response()

  @decorators.action(
    detail=True,
    methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def modify(self, request, pk=None):
    item = self.get_object()
    if request.method == 'GET':
      return response.Response()
    form = self.get_form()
    instance = self.save_form(request, form)
    if instance:
      return callback_or_redirect(request,
        self.get_model_name()+'-detail',
        pk=pk,
      )
    return response.Response()

  @decorators.action(
    detail=True,
    methods=['get'],
  )
  def remove(self, request, pk=None):
    item = self.get_object()
    self.check_object_permissions(request, item)
    item.delete()
    return callback_or_redirect(request,
      self.get_model_name()+'-list'
    )

  def get_add_template_context(self, request, context):
    form = self.get_form()
    return dict(context,
      form=form,
    )

  def get_modify_template_context(self, request, context):
    item = self.get_object()
    form = self.get_form()
    return dict(context,
      item=item,
      form=form,
    )

  def get_retrieve_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    item = self.get_object()

    return dict(context,
      item=item,
      children={
        child: paginator_cls(
          child_attr,
          page_size,
        ).get_page(
          request.GET.get('page')
        )
        for child, child_attr in self.get_model_children(item)
      },
    )

  def get_list_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']
    form = self.get_form()

    return dict(context,
      form=form,
      items=paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    )

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
  def stats(self, request, pk=None):
    item = self.get_object()
    self.check_object_permissions(request, item)
    return response.Response()
  
  def get_stats_template_context(self, request, context):
    item = self.get_object()
    return dict(context,
      item=self.get_object(),
      plots=[
        'TablePlot',
        'RubricPieChart',
        'RubricsInProjectsOverlay',
        'DigitalObjectBarBreakdown',
      ]
    )

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
    return models.Assessment.objects.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(assessor=self.request.user)
    )

  def get_assessment(self):
    ''' Find or create this specific assessment object
    '''
    target_id = self.request.GET.get('target', None)
    rubric_id = self.request.GET.get('rubric', None)
    project_id = self.request.GET.get('project', None)

    # Is there enough information to get an object?
    if not target_id or not rubric_id:
      return None

    # Get or create the assessment
    if project_id:
      assessment = get_or_create(models.Assessment,
        project=models.Project.objects.get(id=project_id),
        target=models.DigitalObject.objects.get(id=target_id),
        rubric=models.Rubric.objects.get(id=rubric_id),
        assessor=self.request.user,
        methodology='user',
      )
    else:
      assessment = get_or_create(models.Assessment,
        project=None,
        target=models.DigitalObject.objects.get(id=target_id),
        rubric=models.Rubric.objects.get(id=rubric_id),
        assessor=self.request.user,
        methodology='user',
      )

    # Ensure answers are created
    for metric in assessment.rubric.metrics.all():
      answer = get_or_create(models.Answer,
        assessment=assessment,
        metric=metric,
      )
    
    # TODO: ensure metrics no longer associated are removed
    
    return assessment
  
  def get_assessment_form(self, initial={}):
    return forms.AssessmentForm(
      dict(
        self.request.GET.dict(),
        **initial,
        **self.request.POST.dict(),
      )
    )
  
  def get_answer_forms(self, assessment):
    ''' Get the answers associated with the assessment object
    '''
    if assessment:
      initial = {}
      if self.request.method == 'POST':
        initial = self.request.POST.dict()
      else:
        auto_assessment_results = Assessment.perform(
          rubric=assessment.rubric,
          target=assessment.target,
        )
        initial = {
          '%s-%s' % (answer.metric.id, key): attr if not getattr(answer, key) else getattr(answer, key)
          for answer in assessment.answers.all()
          for key, attr in auto_assessment_results.get('metric:%d' % (answer.metric.id), {}).items()
          if attr or getattr(answer, key)
        }
      initial = dict(self.request.GET.dict(), **initial)
      return [
        forms.AnswerForm(
          initial,
          instance=answer,
          prefix=answer.metric.id,
        )
        for answer in assessment.answers.all()
      ]
  
  def get_suggestions(self):
    ''' Prepare likely possibilities as suggestions
    '''
    target = self.request.GET.get('target')
    rubric = self.request.GET.get('rubric')
    project = self.request.GET.get('project')
    q = self.request.GET.get('q', '')

    # Prepare target queries
    target_q = {
      '__'.join(k.split('__')[1:]): v
      for k, v in self.request.GET.items()
      if '__' in k and k.split('__')[0] == 'target'
    }

    # Strip protocol from url for search
    target_url = target_q.get('url')
    if target_url:
      target_url = ''.join(target_url.split('://')[1:])
      target_q['url'] = target_url

    target_filters = [
      lambda q, _k=k+'__icontains', _v=v: Q(**{_k: _v})
      for k, v in target_q.items()
    ]

    if target:
      targets = models.DigitalObject.objects.filter(id=target)
    else:
      if target_filters:
        targets = models.DigitalObject.objects.filter(
          reduce(
            lambda F, f, q=q: (F|f(q)) if F is not None else f(q),
            target_filters,
            None,
          )
        ).order_by('id').distinct()
      else:
        targets = None

      if not targets:
        targets = search.DigitalObjectSearchVector().query(q)

    if rubric:
      if target:
        rubrics = targets.first().rubrics.all()
      else:
        rubrics = models.Rubric.objects.filter(id=rubric)
    else:
      rubrics = None
      if target:
        rubrics = targets.first().rubrics.all()
      if rubrics is None or not rubrics.exists():
        rubrics = models.Rubric.objects.all()
      if rubrics.count() == 1:
        rubric = rubrics.first().id

    if project:
      if target:
        projects = targets.first().projects.all()
      else:
        projects = models.Project.objects.filter(id=project)
    else:
      projects = None
      if target:
        projects = targets.first().projects.all()
      if projects is None or projects.exists():
        projects = models.Project.objects.all()
      if projects.count() == 1:
        project = projects.first().id

    return {
      'target': target,
      'rubric': rubric,
      'project': project,
      'targets': targets[:10],
      'rubrics': rubrics[:10],
      'projects': projects[:10],
    }

  def save_answer_forms(self, answer_forms):
    ''' Save answer forms if they are all valid
    '''
    if not all([
      answer_form.is_valid()
      for answer_form in answer_forms
    ]):
      return False
    for answer_form in answer_forms:
      answer_form.save()
    return True

  @decorators.action(
    detail=False, methods=['get'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def prepare(self, request, **kwargs):
    ''' Prepare assessment form
    '''
    self.check_permissions(request)
    return response.Response()

  @decorators.action(
    detail=False, methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def perform(self, request, **kwargs):
    ''' Create assessment form or submit if valid
    '''
    self.check_permissions(request)
    assessment = self.get_assessment()
    if not assessment:
      return redirect_with_params(
        request,
        'assessment-prepare'
      )
    if request.method == 'POST':
      answer_forms = self.get_answer_forms(assessment)
      if self.save_answer_forms(answer_forms):
        return callback_or_redirect(request,
          'digital_object-detail',
          pk=assessment.target.id,
        )
    return response.Response()

  def get_prepare_template_context(self, request, context):
    suggestions = self.get_suggestions()
    form = self.get_assessment_form(suggestions)

    return dict(context,
      form=form,
      suggestions=suggestions,
    )

  def get_perform_template_context(self, request, context):
    assessment = self.get_assessment()
    answer_forms = self.get_answer_forms(assessment)
    return dict(context,
      item=assessment,
      answers=[
        {
          'instance': answer,
          'form': answer_form,
        }
        for answer, answer_form in zip(
          assessment.answers.all(), answer_forms
        )
      ]
    )

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
  queryset = models.Assessment.objects.all()
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
      for k in map('='.join, request.GET.items()):
        k = '#' + k
        l = cache.get(k)
        l = json.loads(l) if l else []
        l += [key]
        cache.set(k, json.dumps(l), 60 * 60)

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
        for answer in assessment.answers.all():
          value = answer.value()
          answers[value] = answers.get(value, 0) + 1
      cache.set(key, answers, 60 * 60)
      
    return response.Response(answers)
