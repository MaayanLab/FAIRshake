import json
from django.shortcuts import render, redirect, HttpResponse
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from FAIRshakeAPI.models import (
  DigitalObject,
  Project,
  Assessment,
  Answer,
  Rubric,
  Metric,
)

top_projects = Project.objects.annotate(n_objs=models.Count('digital_objects')).order_by('-n_objs').all()

def index(request):
  ''' FAIRshakeHub Home Page
  '''
  return render(request, 'index.html', dict(
    top_projects=top_projects[:4],
    active_page='index',
    current_user=request.user,
  ))

def projects(request):
  return render(request, 'projects.html', dict(
    projects=top_projects,
    active_page='projects',
    current_user=request.user,
  ))

def start_project(request):
  return render(request, 'start_project.html', dict(
    active_page='start_project',
    current_user=request.user,
  ))

def bookmarklet(request):
  return render(request, 'bookmarklet.html', dict(
    active_page='bookmarklet',
    current_user=request.user,
  ))

def chrome_extension(request):
  return render(request, 'chrome_extension.html', dict(
    active_page='chrome_extension',
    current_user=request.user,
  ))

@login_required
def resources(request, project):
  project = Project.objects.get(id=project)
  resources = project.digital_objects.filter(
    assessments__isnull=False,
  ).annotate(
    n_assessments=models.Count('id'),
  )
  # TODO: there should be ab etter way
  user_resources = [v['id'] for v in resources.filter(
    assessments__assessor=request.user.id,
  ).values('id')]
  # TODO: project_resources and project_evaluated_resources are similar enough to be merged.
  return render(request, 'project_resources.html', dict(
    project=project,
    resources=resources,
    user_resources=user_resources,
    current_user=request.user,
  ))

@login_required
def my_evaluations(request, project):
  project = Project.objects.get(id=project)
  # TODO: rename resources
  # Fetch all user-assessed digital objects and count the number of assessments.
  resources = project.digital_objects.filter(
    assessments__assessor=request.user.id,
    assessments__isnull=False,
  ).annotate(
    # NOTE: this count is for the number of user assessments
    n_assessments=models.Count('id'),
  )

  # TODO: project_resources and project_evaluated_resources are similar enough to be merged.
  return render(request, 'project_evaluated_resources.html', dict(
    project=project,
    resources=resources,
    current_user=request.user,
  ))

@login_required
def evaluation(request):
  # TODO: this function is a mess and hard to follow
  resource_id = request.GET.get('resource_id', request.POST.get('resource_id'))
  obj = DigitalObject.objects.get(id=resource_id)
  # TODO: this won't work when multiple projects have the same object
  #       it should be passed.
  project = obj.projects.first()

  if request.method == 'GET':
    rubrics = Rubric.objects.all()
    return render(request, 'evaluation.html', dict(
      resource=DigitalObject.objects.get(id=resource_id),
      rubrics=rubrics,
      rubric_ids=[rubric.id for rubric in rubrics],
      current_user_assessment=Assessment.objects.filter(target=resource_id, assessor=request.user.id),
      current_user=request.user,
    ))
  else:
    resource_id = request.POST.get('resource_id')
    rubric_ids = json.loads(request.POST.get('rubric_ids'))
    # rubrics = [rubric.get(id=rubric_id) for rubric_id in rubric_ids]
    rubrics = [Rubric.objects.get(id=rubric_id) for rubric_id in rubric_ids]
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
      assessment = Assessment(
        project=project, # TODO
        target=DigitalObject.objects.get(id=resource_id),
        assessor=request.user.id,
        rubric=rubric,
      )
      assessment.save()
      
      for metric in rubric.metrics.all():
        Answer(
          assessment=assessment,
          metric=metric,
          answer=request.POST.get(metric.id, ''),
          # comment=
          # url_comment=
        ).save()
      # assessment.post(
      #   Assessment(
      #     target=resource_id,
      #     assessor=request.user.id,
      #     rubric=rubric.id,
      #     answers=answers,
      #   )
      # )
    # project = get_project_id(first(repository.get(resource_id)))
    return redirect('/project/{:d}/resources'.format(project.id))

@login_required
def evaluated_projects(request):
  # Fetch all projects for which this user has assessments for
  projects = Project.objects.filter(
    assessments__isnull=False,
    assessments__assessor=request.user.id,
  ).distinct()

  return render(request, 'evaluated_projects.html', dict(
    evaluated_projects=projects,
    current_user=request.user,
  ))

def register(request):
  # TODO
  username = request.POST.get('username')
  email = request.POST.get('email')
  password = request.POST.get('password')
  if all(
    element is not None
    for element in [
      username,
      email,
      password,
     ]
   ):
    try:
      user = User.objects.create_user(
        username,
        email,
        password,
      )
      user.save()
    except Exception as e:
      raise forms.ValidationError(e)
  return render(request, 'register.html', dict(
    current_user=request.user,
    active_page='register',
  ))

def login(request):
  # TODO
  # return render(request, 'oidc_authentication_init')
  username = request.POST.get('username')
  password = request.POST.get('password')
  if username is not None and password is not None:
    auth = authenticate(request,
      username=username,
      password=password,
    )
    if auth is not None:
      login(request, auth)
      return redirect('/', code=302)
  return render(request, 'login.html', dict(
    active_page='login',
  ))

def logout(request):
  # TODO
  logout(request)
  return redirect('/', code=302)
