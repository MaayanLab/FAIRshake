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

  def get_object(self):
    ''' For some reason I needed to rewrite this, the upstream version is weird.
    '''
    obj = shortcuts.get_object_or_404(self.get_model(), **self.kwargs)
    self.check_object_permissions(self.request, obj)
    return obj

  def get_model(self):
    return self.model
  
  def get_model_name(self):
    return self.get_model()._meta.verbose_name_raw
  
  def get_model_children(self, obj):
    for child in self.get_model().MetaEx.children:
      child_attr = getattr(obj, child)
      yield (child_attr.model._meta.verbose_name_raw, child_attr.all())

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
          child_attr,
          page_size,
        ).get_page(
          request.GET.get('page')
        )
        for child, child_attr in self.get_model_children(item)
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
  def add(self, request, pk=None, **kwargs):
    self.check_permissions(request)
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST)
    instance = self.save_form(request, form)
    return callback_or_redirect(request,
      self.get_model_name()+'-detail',
      pk=instance.id,
    )

  @decorators.action(
    detail=True,
    methods=['get', 'post'],
    renderer_classes=[CustomTemplateHTMLRenderer],
  )
  def modify(self, request, pk=None):
    item = self.get_object()
    if request.method == 'GET':
      return response.Response()
    form_cls = self.get_form()
    form = form_cls(request.POST, instance=item)
    instance = self.save_form(request, form)
    return callback_or_redirect(request,
      self.get_model_name()+'-detail',
      pk=pk,
    )

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
  lookup_field = 'pk'

  def get_queryset(self):
    if self.request.user.is_anonymous:
      return models.Assessment.objects.none()
    return models.Assessment.objects.filter(
      Q(target__authors=self.request.user)
      | Q(project__authors=self.request.user)
      | Q(assessor=self.request.user)
    )
  
  def save_form(self, request, form):
    assessment = form.save(commit=False)
    assessment.assessor = request.user
    assessment.methodology = 'user'
    assessment.save()
    if not assessment.answers.exists():
      for metric in assessment.rubric.metrics.all():
        answer = models.Answer(
          assessment=assessment,
          metric=metric,
        )
        answer.save()

    for answer in assessment.answers.all():
        answer_form = forms.AnswerForm(
          request.POST,
          instance=answer,
          prefix=answer.metric.id,
        )
        answer_form.save()

    cache.delete_many([
      ','.join(map('='.join, request.GET.items())),
      *map('='.join, request.GET.items()),
    ])

    return assessment
  
  def get_template_context(self, request, context):
    if self.action in ['modify', 'retrieve']:
      assessment = self.get_object()
      assessment_form = forms.AssessmentForm(instance=assessment)

      answers = []
      for answer in assessment.answers.all():
        answer_form = forms.AnswerForm(
          prefix=answer.metric.id,
          instance=answer,
        )
        answers.append({
          'form': answer_form,
          'instance': answer,
        })

      return dict(context, **{
        'model': self.get_model_name(),
        'action': self.action,
        'form': assessment_form,
        'item': assessment,
        'answers': answers,
      })
    elif self.action in ['add']:
      assessment_form = forms.AssessmentForm(request.GET)
      prepare = request.GET.get('prepare')
      if not assessment_form.is_valid() or prepare is not None:
        target = request.GET.get('target')
        rubric = request.GET.get('rubric')
        project = request.GET.get('project')
        q = request.GET.get('q', '')

        if target is not None:
          targets = models.DigitalObject.objects.filter(id=target)
        else:
          targets = search.DigitalObjectSearchVector().query(q)

        if rubric is not None:
          rubrics = models.Rubric.objects.filter(id=target)
        else:
          rubrics = None
          if target is not None:
            rubrics = targets.first().rubrics.all()
          if rubrics is None or not rubrics.exists():
            rubrics = models.Rubric.objects.all()
          if rubrics.count() == 1:
            rubric = rubrics.first().id

        if project is not None:
          projects = models.Project.objects.filter(id=project)
        else:
          projects = None
          if target is not None:
            projects = targets.first().projects.all()
          if projects is None or projects.exists():
            projects = models.Project.objects.all()
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

        if prepare is not None or not assessment_form.is_valid():
          assessment_form.fields['target'] = ModelChoiceField(queryset=targets, required=True)
          assessment_form.fields['rubric'] = ModelChoiceField(queryset=rubrics, required=True)
          assessment_form.fields['project'] = ModelChoiceField(queryset=projects, required=False)

          return {
            'model': self.get_model_name(),
            'action': 'prepare',
            'form': assessment_form,
          }

      assessment = assessment_form.save(commit=False)
      assessment.assessor = request.user

      answers = []
      for metric in assessment.rubric.metrics.all():
        answer = models.Answer(
          assessment=assessment,
          metric=metric,
        )
        answer_form = forms.AnswerForm(
          request.GET,
          prefix=metric.id,
          instance=answer,
        )
        answers.append({
          'form': answer_form,
          'instance': answer,
        })

      return dict(context, **{
        'model': self.get_model_name(),
        'action': self.action,
        'form': assessment_form,
        'item': assessment,
        'answers': answers,
      })
    return super().get_template_context(request, context)

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
        for answer in models.Answer.objects.filter(
          assessment=assessment.id,
        ):
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
        for answer in assessment.answers.all():
          value = answer.value()
          answers[value] = answers.get(value, 0) + 1
      cache.set(key, answers, 60 * 60)
      
    return response.Response(answers)
