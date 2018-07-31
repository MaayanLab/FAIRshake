import json
from django.shortcuts import render, redirect, HttpResponse
from django.db import models as db
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import generic
from collections import OrderedDict
from FAIRshakeAPI import models, serializers

# TODO: Use Coreapi instead of django models and/or find a coreapi -> django model converter?


def index(request):
  ''' FAIRshakeHub Home Page
  '''
  return render(request, 'fairshake/index.html')

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html')

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html')

# def projects(request):
#   return render(request, 'fairshake/project/list.html', dict(
#     items=models.Project.objects.all(),
#     model="project",
#   ))

# def project(request, project):
#   project = models.Project.objects.get(id=project)
#   return render(request, 'fairshake/project/retrieve.html', dict(
#     item=project,
#     model="project",
#     children=OrderedDict([
#       ('digital_object', project.digital_objects.all()),
#     ]),
#   ))

@login_required
def project_create(request):
  return render(request, 'fairshake/project/create.html', dict(
    serializer=serializers.ProjectSerializer,
  ))

# def rubrics(request):
#   return render(request, 'fairshake/rubric/list.html', dict(
#     items=models.Rubric.objects.all(),
#     model="rubric",
#   ))

# def rubric(request, rubric):
#   rubric = models.Rubric.objects.get(id=rubric)
#   return render(request, 'fairshake/rubric/retrieve.html', dict(
#     item=rubric,
#     model="rubric",
#     children=OrderedDict([
#       ('metric', rubric.metrics.all()),
#       ('digital_object', rubric.digital_objects.all()),
#     ]),
#   ))

@login_required
def rubric_create(request):
  return render(request, 'fairshake/rubric/create.html', dict(
    serializer=serializers.RubricSerializer,
  ))

# def digital_objects(request):
#   return render(request, 'fairshake/digital_object/list.html', dict(
#     items=models.DigitalObject.objects.all(),
#     model="digital_object",
#   ))

# def digital_object(request, digital_object):
#   digital_object = models.DigitalObject.objects.get(id=digital_object)
#   return render(request, 'fairshake/digital_object/retrieve.html', dict(
#     item=digital_object,
#     model="digital_object",
#     children=OrderedDict([
#       ('rubric', digital_object.rubrics.all()),
#       ('project', digital_object.projects.all()),
#     ]),
#   ))

@login_required
def digital_object_create(request):
  return render(request, 'fairshake/digitalobject/create.html', dict(
    serializer=serializers.DigitalObjectSerializer,
  ))

# def metrics(request):
#   return render(request, 'fairshake/metric/list.html', dict(
#     items=models.Metric.objects.all(),
#     model="metric",
#   ))

# def metric(request, metric):
#   metric = models.Metric.objects.get(id=metric)
#   return render(request, 'fairshake/metric/retrieve.html', dict(
#     item=metric,
#     model="metric",
#     children=OrderedDict([
#       ('rubric', metric.rubrics.all()),
#     ]),
#   ))

@login_required
def metric_create(request):
  return render(request, 'fairshake/metric/create.html', dict(
    serializer=serializers.MetricSerializer,
  ))

@login_required
def assessment_create(request):
  return render(request, 'fairshake/assessment/create.html', dict(
    serializer=serializers.AssessmentSerializer,
  ))
