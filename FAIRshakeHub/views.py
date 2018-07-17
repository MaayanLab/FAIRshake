import json
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Count, F
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

def top_projects():
  ''' Top Projects, projects with the largest number of digital objects '''
  return Project \
    .objects \
    .annotate(n_objs=Count('digital_objects')) \
    .order_by('-n_objs') \
    .all()

def index(request):
  ''' FAIRshakeHub Home Page
  '''
#   return render(request, 'index.html', dict(
#   top_projects=repository.get(limit=4),
#   current_user=request.user,
#   )
  return render(request, 'index.html', dict(
    top_projects=top_projects()[:4],
    active_page='index',
    current_user=request.user,
  ))

def projects(request):
#   return render(request, 'projects.html', dict(
#     projects=repository.get(tags=['project']),
#     current_user=request.user,
#   )
  return render(request, 'projects.html', dict(
    projects=top_projects(),
    active_page='projects',
    current_user=request.user,
  ))

def start_project(request):
#   return render(request, 'start_project.html', dict(
#     current_user=request.user,
#   )
  return render(request, 'start_project.html', dict(
    active_page='start_project',
    current_user=request.user,
  ))

def bookmarklet(request):
#   return render(request, 'bookmarklet.html', dict(
#   current_user=request.user,
#   )
  return render(request, 'bookmarklet.html', dict(
    active_page='bookmarklet',
    current_user=request.user,
  ))

def chrome_extension(request):
#   return render(request, 'chrome_extension.html', dict(
#   current_user=request.user,
#   )
  return render(request, 'chrome_extension.html', dict(
    active_page='chrome_extension',
    current_user=request.user,
  ))

@login_required
def resources(request, project):
  resources = Project.objects.get(id=project).digital_objects.all()
  # resources = repository.get(tags=['project:{:s}'.format(project)])
  current_user_assessed_resources = [
    resource.id for resource in resources
    if Assessment.objects.filter(target=resource.id, assessor=request.user.id)
    # if assessment.get(object=resource.id, user=current_user()['sub']) != []
  ]
  assessment_count = {
    resource.id: len(Assessment.objects.filter(target=resource.id))
    # resource.id: len(assessment.get(object=resource.id))
    for resource in resources
  }
  aggregate_scores = {
    resource.id: 0
    # resource.id: score.get(object=resource.id, kind='text/html')
    for resource in resources
  }
  return render(request, 'project_resources.html', dict(
    project=Project.objects.get(id=project),
    # project=first(repository.get(id='{:s}'.format(project), limit=1)),
    resources=resources,
    aggregate_scores=aggregate_scores,
    assessment_count=assessment_count,
    current_user_assessed_resources=current_user_assessed_resources,
    current_user=request.user,
  ))

@login_required
def my_evaluations(request, project):
  current_user_assessed_resources = [
    resource for resource in Project.objects.get(id=project).digital_objects.all()
    # resource for resource in repository.get(tags=['project:{:s}'.format(project)])
    if Assessment.objects.filter(target=resource.id, assessor=request.user.id)
    # if assessment.get(object=resource.id, user=current_user()['sub']) != []
  ]
  assessment_count = {
    resource.id: Assessment.objects.filter(target=resource.id).count()
    # resource.id: len(assessment.get(object=resource.id))
    for resource in current_user_assessed_resources
  }
  aggregate_scores = {
    resource.id: 0
    # resource.id: score.get(object=resource.id, kind='text/html')
    for resource in current_user_assessed_resources
  }
  current_user_scores = {
    resource.id: 0
    # resource.id: score.get(object=resource.id, user=current_user()['sub'], kind='text/html')
    for resource in current_user_assessed_resources
  }
  return render(request, 'project_evaluated_resources.html', dict(
    project=Project.objects.get(id=project),
    # project=first(repository.get(id='{:s}'.format(project), limit=1)),
    aggregate_scores=aggregate_scores,
    current_user_scores=current_user_scores,
    assessment_count=assessment_count,
    current_user_assessed_resources=current_user_assessed_resources,
    current_user=request.user,
  ))

@login_required
def evaluation(request):
  resource_id = request.GET.get('resource_id', request.POST.get('resource_id'))
  obj = DigitalObject.objects.get(id=resource_id)
  # TODO: this won't work when multiple projects have the same object
  #       it should be passed.
  project = obj.projects.first()

  if request.method == 'GET':
    rubrics = Rubric.objects.all()
    return render(request, 'evaluation.html', dict(
      resource=DigitalObject.objects.get(id=resource_id),
      # resource=first(repository.get(id=resource_id, limit=1)),
      rubrics=rubrics,
      # rubrics=rubric.get(),
      rubric_ids=[rubric.id for rubric in rubrics],
      # rubric_ids=[rubric.id for rubric in rubric.get()],
      current_user_assessment=Assessment.objects.filter(target=resource_id, assessor=request.user.id),
      # current_user_assessment=assessment.get(object=resource_id, user=current_user()['sub']),
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
  evaluated_projects_id_list = {
    Project.objects.filter(digital_objects__has=assessment_each.object)
    # first(
    #   repository.get(
    #     id=get_project_id(
    #       first(
    #         repository.get(id=assessment_each.object)
    #       )
    #     )
    #   )
    # ).id
    # for assessment_each in assessment.get(user=current_user()['sub'])
    for assessment_each in Assessment.objects.filter(assessor=request.user.id)
  }
  evaluated_projects = [
    DigitalObject.object.get(id=id_each)
    # first(repository.get(id=id_each))
    for id_each in evaluated_projects_id_list
  ]
  return render(request, 'evaluated_projects.html', dict(
    evaluated_projects=evaluated_projects,
    current_user=request.user,
  ))

def register(request):
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
