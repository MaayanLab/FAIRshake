from django.shortcuts import render, HttpResponse
from .models import Project, Resource
from django.db.models import Count, F

def top_projects():
    ''' Top Projects, projects with the largest number of resources '''
    return Project \
        .objects \
        .annotate(n_resources=Count('resources')) \
        .order_by('-n_resources') \
        .all()

def index(request):
    ''' FAIRshakeHub Home Page
    '''
    return render(request, 'index.html', dict(
        top_projects=top_projects()[:4],
    ))

def projects(request):
    return render(request, 'projects.html', dict(
        projects=top_projects(),
    ))

def start_project(request):
    return render(request, 'start_project.html')

def bookmarklet(request):
    return render(request, 'bookmarklet.html')

def chrome_extension(request):
    return render(request, 'chrome_extension.html')

def register(request):
    # TODO: handle post to FAIRshakeAPI
    return render(request, 'register.html')

def login(request):
    # TODO: handle post to FAIRshakeAPI
    return render(request, 'login.html')

def new_evaluation(request):
    # TODO: handle post to FAIRshakeAssessments
    return render(request, 'new_evaluation.html', dict(
        resource=Resource.objects.get(id=0)
    ))
