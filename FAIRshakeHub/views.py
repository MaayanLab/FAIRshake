import json
from django.shortcuts import render, redirect, HttpResponse
from django.db import models as db
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from FAIRshakeAPI import models

# TODO: Use Coreapi instead of django models and/or find a coreapi -> django model converter?

def top_projects():
  return models.Project.objects.annotate(n_objs=db.Count('digital_objects')).order_by('-n_objs').all()

def index(request):
  ''' FAIRshakeHub Home Page
  '''
  return render(request, 'fairshake/index.html', dict(
    top_projects=top_projects()[:4],
    active_page='index',
    current_user=request.user,
  ))

def projects(request):
  return render(request, 'fairshake/projects.html', dict(
    projects=top_projects(),
    active_page='projects',
    current_user=request.user,
  ))

def start_project(request):
  return render(request, 'fairshake/start_project.html', dict(
    active_page='start_project',
    current_user=request.user,
  ))

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html', dict(
    active_page='bookmarklet',
    current_user=request.user,
  ))

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html', dict(
    active_page='chrome_extension',
    current_user=request.user,
  ))

@login_required
def resources(request, project):
  project = models.Project.objects.get(id=project)
  resources = project.digital_objects.annotate(
    n_assessments=db.Count('id'),
  )
  # TODO: there should be a better way
  user_resources = [v['id'] for v in resources.filter(
    assessments__assessor=request.user.id,
  ).values('id')]
  # TODO: project_resources and project_evaluated_resources are similar enough to be merged.
  return render(request, 'fairshake/project_resources.html', dict(
    project=project,
    resources=resources,
    user_resources=user_resources,
    current_user=request.user,
  ))

@login_required
def my_evaluations(request, project):
  project = models.Project.objects.get(id=project)
  # TODO: rename resources
  # Fetch all user-assessed digital objects and count the number of assessments.
  resources = project.digital_objects.filter(
    assessments__assessor=request.user.id,
    assessments__isnull=False,
  ).annotate(
    # NOTE: this count is for the number of user assessments
    n_assessments=db.Count('id'),
  )

  # TODO: project_resources and project_evaluated_resources are similar enough to be merged.
  return render(request, 'fairshake/project_evaluated_resources.html', dict(
    project=project,
    resources=resources,
    current_user=request.user,
  ))

@login_required
def evaluation(request):
  # TODO: this function is a mess and hard to follow
  resource_id = request.GET.get('resource_id', request.POST.get('resource_id'))
  obj = models.DigitalObject.objects.get(id=resource_id)
  # TODO: this won't work when multiple projects have the same object
  #       it should be passed.
  project = obj.projects.first()

  if request.method == 'GET':
    rubrics = models.Rubric.objects.all()
    return render(request, 'fairshake/evaluation.html', dict(
      resource=models.DigitalObject.objects.get(id=resource_id),
      rubrics=rubrics,
      rubric_ids=[rubric.id for rubric in rubrics],
      current_user_assessment=models.Assessment.objects.filter(target=resource_id, assessor=request.user.id),
      current_user=request.user,
    ))
  else: # TODO: post directly to API
    resource_id = request.POST.get('resource_id')
    rubric_ids = json.loads(request.POST.get('rubric_ids'))
    # rubrics = [rubric.get(id=rubric_id) for rubric_id in rubric_ids]
    rubrics = [models.Rubric.objects.get(id=rubric_id) for rubric_id in rubric_ids]
    for rubric in rubrics:
      answers = [
        {
          'id': metric.id,
          # 'id': criterion.id,
          'value': request.POST.get(metric.id)
          # 'value': request.POST.get(criterion.id)
        }
        # for criterion in rubric.criteria
        for metric in rubric.metrics.all()
      ]
      assessment = models.Assessment(
        project=project,
        target=models.DigitalObject.objects.get(id=resource_id),
        assessor=request.user.id,
        rubric=rubric,
      )
      assessment.save()
      
      for metric in rubric.metrics.all():
        models.Answer(
          assessment=assessment,
          metric=metric,
          answer=request.POST.get(metric.id, ''),
          # comment=,
          # url_comment=,
        ).save()
    # TODO: redirect somewhere else if we don't have access to the project
    return redirect('/project/{:d}/resources'.format(project.id))

@login_required
def evaluated_projects(request):
  # Fetch all projects for which this user has assessments for
  projects = models.Project.objects.filter(
    assessments__isnull=False,
    assessments__assessor=request.user.id,
  ).distinct()

  return render(request, 'fairshake/evaluated_projects.html', dict(
    evaluated_projects=projects,
    current_user=request.user,
  ))
