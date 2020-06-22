# TODO: split up into abstract API implementations

import json
import logging
from . import serializers, filters, models, forms, search
from .permissions import ModelDefinedPermissions
from .assessments import Assessment
from .util import query_dict
from django import shortcuts, forms as django_forms
from django.http import HttpResponse
from django.utils.html import escape
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Avg, Count
from django.forms import ModelChoiceField
from django.urls import reverse
from rest_framework import views, viewsets, schemas, response, mixins, decorators, renderers, permissions
from functools import reduce
from collections import defaultdict, OrderedDict

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
  objects = model.objects.filter(**kwargs)
  if objects.count() == 0:
    obj = model(**{
      k: v for k, v in kwargs.items() if v
    })
    obj.save()
    return obj
  if objects.count() > 1:
    logging.warn('get_or_create got more than 1 object. (%s)' % (kwargs))
  return objects.last()

def redirect_with_params(request, *args, **kwargs):
  return shortcuts.redirect(
    reverse(*args, **kwargs) + '?' + request.GET.urlencode()
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
      popup=self.request.GET.get('_popup', None),
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
      form = form_cls(initial=query_dict(
        self.request.GET,
        authors=self.request.user,
      ))
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
    detail=True, methods=['get'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def assessments(self, request, pk=None, **kwargs):
    self.check_permissions(request)
    return response.Response()

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
      popup = request.GET.get('_popup', None)
      if popup is not None:
        return HttpResponse('''
          <script type="text/javascript">
            opener.dismissAddAnotherPopupEx(
                window,
                "{pk}",
                "{obj}"
            );
          </script>
        '''.format(
          pk=escape(instance.pk),
          obj=escape(repr(instance))
        ))
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
      children=OrderedDict([
        (child, paginator_cls(
          child_attr,
          page_size,
        ).get_page(
          request.GET.get('page')
        ))
        for child, child_attr in self.get_model_children(item)
      ]),
    )

  def get_list_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']

    return dict(context,
      items=paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    )
  
  def get_assessments_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['ASSESSMENTS_PAGE_SIZE']

    item = self.get_object()
    model = self.get_model_name()
    if model == 'digital_object':
      q = Q(target=item)
    elif model == 'metric':
      q = Q(rubric__metrics=item)
    else:
      q = Q(**{ model: item })

    assessments = models.Assessment.objects.filter(q)

    if model == 'metric':
      metrics = [item]
    elif model == 'rubric':
      metrics = item.metrics.all()
    else:
      metrics = models.Metric.objects.filter(id__in=assessments.values_list('answers__metric', flat=True).order_by().distinct())

    assessments_paginated = paginator_cls(
      assessments,
      page_size
    ).get_page(
      request.GET.get('page')
    )

    answers = {
      '%d-%d' % (assessment.id, answer.metric_id): answer
      for assessment in assessments_paginated.object_list
      for answer in (assessment.answers.all() if model == 'rubric' else (
        assessment.answers.filter(metric__in=metrics)
      ))
    }

    return dict(context,
      item=item,
      items=assessments_paginated,
      metrics=metrics,
      answers=answers,
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
        # 'TablePlot',
        'RubricsInProjectsOverlay',
        'RubricPieChart',
        'DigitalObjectBarBreakdown',
        'RubricsByMetricsBreakdown'
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
  filter_class = filters.AssessmentFilterSet

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
        published=False,
        project=models.Project.objects.get(id=project_id),
        target=models.DigitalObject.objects.get(id=target_id),
        rubric=models.Rubric.objects.get(id=rubric_id),
        assessor=self.request.user,
        methodology='user',
      )
    else:
      assessment = get_or_create(models.Assessment,
        published=False,
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
      query_dict(
        self.request.GET,
        initial,
        self.request.POST,
      )
    )
  
  def get_answer_forms(self, assessment):
    ''' Get the answers associated with the assessment object
    '''
    if assessment:
      initial = query_dict(
        {
          '%s-%s' % (answer.metric_id, key): getattr(answer, key)
          for answer in assessment.answers.all()
          for key in ['answer', 'comment', 'url_comment']
          if getattr(answer, key, None) is not None
        },
        self.request.GET,
      )

      if self.request.method == 'POST':
        initial = query_dict(initial, self.request.POST)
      else:
        auto_assessment_results = Assessment.perform(
          rubric=assessment.rubric,
          target=assessment.target,
        )
        for answer in assessment.answers.all():
          for key, attr in auto_assessment_results.get('metric:%d' % (answer.metric_id), {}).items():
            k = '%s-%s' % (answer.metric_id, key)
            if attr is not None and initial.get(k) is not None:
              initial[k] = attr

      return [
        forms.AnswerForm(
          initial,
          instance=answer,
          prefix=answer.metric_id,
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

    target_url = target_q.get('url')
    target_filters = [
      lambda q, _k=k+('__url_similar' if k == 'url' else '__icontains'), _v=v: Q(**{_k: _v})
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
      
      if targets.count() == 1:
        target = targets.first().id

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
      if projects is None or not projects.exists():
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
    for answer_form in answer_forms:
      if answer_form.is_valid():
        answer_form.save()
      # else:
      #   answer_form.instance.delete()
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
        published = json.loads(request.POST.get('published'))
        if type(published) == bool and published == True:
          assessment.published = True
          assessment.save()
        return callback_or_redirect(request,
          'digital_object-detail',
          pk=assessment.target_id,
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
    # TODO: redirect to a more intuitive location
    return callback_or_redirect(request, 'index')

  def get_list_template_context(self, request, context):
    paginator_cls = self.paginator.django_paginator_class
    page_size = settings.REST_FRAMEWORK['VIEW_PAGE_SIZE']

    return dict(context,
      items=paginator_cls(
        self.filter_queryset(
          self.get_queryset()
        ),
        page_size,
      ).get_page(
        request.GET.get('page')
      ),
    )

  def get_prepare_template_context(self, request, context):
    suggestions = self.get_suggestions()
    form = self.get_assessment_form(suggestions)

    return dict(context,
      form=form,
      suggestions=suggestions,
    )
  
  def get_retrieve_template_context(self, request, context):
    assessment = self.get_object()
    if not assessment:
      return context
    return dict(
      item=assessment
    )

  def get_perform_template_context(self, request, context):
    assessment = self.get_assessment()
    if not assessment:
      return context
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
  filter_class = filters.AssessmentRequestFilterSet

  def save_form(self, request, form):
    instance = form.save(commit=False)
    instance.requestor = request.user
    instance.save()
    return instance

def agg_values(values):
  values_filtered = [
    v for v in values
    if v != float('nan') and v is not None
  ]
  if len(values_filtered) > 0:
    return sum(values_filtered) / len(values_filtered)
  else:
    return None

class ScoreViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
  ):
  ''' Request an score for a digital resource
  '''
  serializer_class = serializers.AssessmentSerializer
  filter_class = filters.ScoreFilterSet
  pagination_class = None

  def get_queryset(self):
    if self.request.user.is_anonymous:
      return models.Assessment.objects.filter(published=True)
    return models.Assessment.objects.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(assessor=self.request.user)
      | Q(published=True)
    )

  def _retrieve(self, assessment):
    '''
    Generate scores for a single assessment by id.
    '''
    result = {
      'scores': {
        assessment.rubric_id: {
          answer.metric_id: answer.answer
        }
        for answer in assessment.answers.all()
      },
      'metrics': {
        answer.metric_id: answer.metric.title
        for answer in assessment.answers.all()
      },
    }
    return response.Response(result)

  def list(self, request):
    '''
    Generate aggregate scores on a per-rubric and per-metric basis.
    '''
    GET = request.GET.dict()

    if GET.get('assessment') is not None:
      return self._retrieve(models.Assessment.objects.get(pk=GET.get('assessment')))

    # Treat `digital_object` as equivalent target here
    if GET.get('digital_object') is not None:
      GET['target'] = GET['digital_object']
      del GET['digital_object']
  
    key = ','.join(map('='.join, GET.items()))
    # result = cache.get(key)
    result = None

    if result is None:
      scores = {}
      metrics = {}

      targets = set()
      rubrics = set()
      projects = set()

      # Ensure we at least capture the elements of the GET request
      if GET.get('target'):
        targets.add(GET['target'])
      if GET.get('rubric'):
        rubrics.add(GET['rubric'])
      if GET.get('project'):
        projects.add(GET['project'])

      assessments = self.filter_queryset(self.get_queryset())

      metrics_set = set()
      scores = defaultdict(lambda: {})
      for row in assessments.values(
        'rubric', 'answers__metric'
      ).order_by().annotate(
        Avg('answers__answer')
      ):
        rubric = row['rubric']
        metric = row['answers__metric']
        metrics_set.add(metric)
        score = row['answers__answer__avg']
        scores[rubric][metric] = score

      metrics_lookup = dict(models.Metric.objects.filter(id__in=metrics_set).values_list('id', 'title'))

      result = {
        'scores': scores,
        'metrics': metrics_lookup,
      }

      # Only cache if we actually got anything
      if metrics and scores:
        cache.set(key, result, 60 * 60)

        # Ensure we can invalidate this cache
        for model, pks in [
          ('target', targets),
          ('rubric', rubrics),
          ('project', projects),
        ]:
          for pk in pks:
            k = '#{model}={pk}'.format(model=model, pk=pk)
            cache.set(
              k, json.dumps(
                list(
                  set(
                    json.loads(
                      cache.get(k, "[]")
                    )
                  ).union([key])
                )
              ),
              60 * 60
            )

    return response.Response(result)

  def retrieve(self, request, pk=None):
    return self._retrieve(self.get_object())

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
      assessments = self.filter_queryset(self.get_queryset())
      result = assessments.order_by().values_list('answers__answer').annotate(Count('answers__answer')).distinct()
      answers = {k: v for k, v in result if k is not None}
      cache.set(key, answers, 60 * 60)

    return response.Response(answers)
