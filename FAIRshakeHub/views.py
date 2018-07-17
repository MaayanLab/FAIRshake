from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Count, F
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from FAIRshakeAPI.models import DigitalObject, Project

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
#   return render_template('index.html',
#     top_projects=repository.get(limit=4),
#     current_user=request.user,
#   )
    return render(request, 'index.html', dict(
        top_projects=top_projects()[:4],
        current_user=request.user,
        active_page='index',
    ))

def projects(request):
#   return render_template('projects.html',
#     projects=repository.get(tags=['project']),
#     current_user=request.user,
#   )
    return render(request, 'projects.html', dict(
        projects=top_projects(),
        active_page='projects',
    ))

def start_project(request):
#   return render_template('start_project.html',
#     current_user=request.user,
#   )
    return render(request, 'start_project.html', dict(
        active_page='start_project',
    ))

def bookmarklet(request):
#   return render_template('bookmarklet.html',
#     current_user=request.user,
#   )
    return render(request, 'bookmarklet.html', dict(
        active_page='bookmarklet',
    ))

def chrome_extension(request):
#   return render_template('chrome_extension.html',
#     current_user=request.user,
#   )
    return render(request, 'chrome_extension.html', dict(
        active_page='chrome_extension',
    ))

@login_required
def resources(request, project):
  resources = repository.get(tags=['project:{:s}'.format(project)])
  current_user_assessed_resources = [
    resource.id for resource in resources
    if assessment.get(object=resource.id, user=current_user()['sub']) != []
  ]
  assessment_count = {
    resource.id: len(assessment.get(object=resource.id))
    for resource in resources
  }
  aggregate_scores = {
    resource.id: score.get(object=resource.id, kind='text/html')
    for resource in resources
  }
  return render_template('project_resources.html',
    project=first(repository.get(id='{:s}'.format(project), limit=1)),
    resources=resources,
    aggregate_scores=aggregate_scores,
    assessment_count=assessment_count,
    current_user_assessed_resources=current_user_assessed_resources,
    current_user=request.user,
  )

@login_required
def my_evaluations(request, project):
  current_user_assessed_resources = [
    resource for resource in repository.get(tags=['project:{:s}'.format(project)])
    if assessment.get(object=resource.id, user=current_user()['sub']) != []
  ]
  assessment_count = {
    resource.id: len(assessment.get(object=resource.id))
    for resource in current_user_assessed_resources
  }
  aggregate_scores = {
    resource.id: score.get(object=resource.id, kind='text/html')
    for resource in current_user_assessed_resources
  }
  current_user_scores = {
    resource.id: score.get(object=resource.id, user=current_user()['sub'], kind='text/html')
    for resource in current_user_assessed_resources
  }
  return render_template('project_evaluated_resources.html',
    project=first(repository.get(id='{:s}'.format(project), limit=1)),
    aggregate_scores=aggregate_scores,
    current_user_scores=current_user_scores,
    assessment_count=assessment_count,
    current_user_assessed_resources=current_user_assessed_resources,
    current_user=request.user,
  )

@login_required
def evaluation(request):
  if request.method == 'GET':
    resource_id = request.args.get('id')
    return render_template('evaluation.html',
      resource=first(repository.get(id=resource_id, limit=1)),
      rubrics=rubric.get(),
      rubric_ids=[rubric.id for rubric in rubric.get()],
      current_user_assessment=assessment.get(object=resource_id, user=current_user()['sub']),
      current_user=request.user,
    )
  else:
    resource_id=request.form.get('resource_id')
    rubric_ids=json.loads(request.form.get('rubric_ids'))
    rubrics=[first(rubric.get(id=rubric_id)) for rubric_id in rubric_ids]
    for rubric in rubrics:
      answers = [
        {
          'id': criterion.id,
          'value': request.form.get(criterion.id)
        }
        for criterion in rubric.criteria
      ]
      assessment.post(
        AssessmentModel(
          object=resource_id,
          user=current_user()['sub'],
          rubric=rubric.id,
          answers=answers,
        )
      )
    project = get_project_id(first(repository.get(resource_id)))
    return redirect('/project/{:s}/resources'.format(project))

@login_required
def evaluated_projects(request):
  evaluated_projects_id_list = {
    first(
      repository.get(
        id=get_project_id(
          first(
            repository.get(id=assessment_each.object)
          )
        )
      )
    ).id
    for assessment_each in assessment.get(user=current_user()['sub'])
  }
  evaluated_projects = [
    first(repository.get(id=id_each))
    for id_each in evaluated_projects_id_list
  ]
  return render_template('evaluated_projects.html',
    evaluated_projects=evaluated_projects,
    current_user=request.user,
  )

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
    logout(request)
    return redirect('/', code=302)
