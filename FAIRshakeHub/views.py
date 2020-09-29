import itertools as it
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from django import http
from django.views.decorators.clickjacking import xframe_options_exempt
from extensions.django.union_paginator import UnionPaginator
from FAIRshakeAPI import search, models, stats

def index(request):
  ''' FAIRshakeHub Home Page
  '''
  q = request.GET.get('q', '')
  filter_projects = bool(request.GET.get('projects', 0))
  filter_digital_objects = bool(request.GET.get('digitalobjects', 0))
  filter_rubrics = bool(request.GET.get('rubrics', 0))
  filter_metrics = bool(request.GET.get('metrics', 0))

  page = request.GET.get('page', 1)
  page_size = settings.REST_FRAMEWORK['SEARCH_PAGE_SIZE']


  vectors = []
  if q:
    if filter_projects:
      vectors.append(search.ProjectSearchVector())
    if filter_digital_objects:
      vectors.append(search.DigitalObjectSearchVector())
    if filter_rubrics:
      vectors.append(search.RubricSearchVector())
    if filter_metrics:
      vectors.append(search.MetricSearchVector())

  paginator = UnionPaginator([
    vector.query(q) for vector in vectors
  ], page_size)

  return render(request, 'fairshake/index.html', dict(
      query=q,
      items=paginator.get_page(page),
      featured=list(it.chain(
        models.Project.objects.filter(id__in=[87]),
        models.Rubric.objects.filter(id__in=[25]),
      )),
      filter_projects=filter_projects,
      filter_digital_objects=filter_digital_objects,
      filter_rubrics=filter_rubrics,
      filter_metrics=filter_metrics,
    )
  )

def contributors_and_partners(request):
  return render(request, 'fairshake/contributors_and_partners.html')

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html')

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html')

def documentation(request):
  return render(request, 'fairshake/documentation/index.html')

def jsonschema_documentation(request):
  return render(request, 'fairshake/documentation/jsonschema.html')

def terms_of_service(request):
  return render(request, 'fairshake/terms_of_service.html')

def privacy_policy(request):
  return render(request, 'fairshake/privacy_policy.html')

def handler(code, message):
  def _handler(request, *args, **kwargs):
    return render(request, 'fairshake/error.html', dict(
      code=code,
      message=message,
    ))
  return _handler

handler400 = handler(400, 'Bad Request')
handler403 = handler(403, 'Permission denied')
handler404 = handler(404, 'Page not Found')
handler500 = handler(500, 'Server error')

def stats_view(request):
  if request.GET.get('model') == 'project':
    try:
      if not models.Project.objects.get(id=request.GET.get('item')).assessments:
        raise Exception()
      page = ''
      for res in {
        'TablePlot': lambda item: stats.TablePlot(item),
        'RubricPieChart': lambda item: stats.RubricPieChart(item.assessments),
        'RubricsByMetricsBreakdown': lambda item: stats.RubricsByMetricsBreakdown(item.assessments),
        'RubricsInProjectsOverlay': lambda item: stats.RubricsInProjectsOverlay(item.assessments),
        'DigitalObjectBarBreakdown': lambda item: stats.DigitalObjectBarBreakdown(item.assessments),
      }.get(request.GET.get('plot'))(models.Project.objects.get(id=request.GET.get('item'))):
        page += res
      return http.HttpResponse(page)
    except:
      return http.HttpResponse('Not enough information was present to construct a plot.')
  return http.HttpResponseNotFound()

@xframe_options_exempt
def framed(request):
  return render(request, 'fairshake/framed.html')
