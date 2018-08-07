import json
from django.shortcuts import render, redirect, HttpResponse
from django.db import models as db
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import generic
from collections import OrderedDict
from FAIRshakeAPI import models, serializers
from . import forms

# TODO: Use Coreapi instead of django models and/or find a coreapi -> django model converter?


def index(request):
  ''' FAIRshakeHub Home Page
  '''
  return render(request, 'fairshake/index.html')

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html')

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html')

@login_required
def project_create(request):
  return render(request, 'fairshake/project/create.html', dict(
    model=models.Project._meta.verbose_name_raw,
    form=forms.ProjectForm(),
  ))

@login_required
def rubric_create(request):
  return render(request, 'fairshake/rubric/create.html', dict(
    model=models.Rubric._meta.verbose_name_raw,
    form=forms.RubricForm(),
  ))

@login_required
def digital_object_create(request):
  return render(request, 'fairshake/digitalobject/create.html', dict(
    model=models.DigitalObject._meta.verbose_name_raw,
    form=forms.DigitalObjectForm(),
  ))

@login_required
def metric_create(request):
  return render(request, 'fairshake/metric/create.html', dict(
    model=models.Metric._meta.verbose_name_raw,
    form=forms.MetricForm(),
  ))

@login_required
def assessment_create(request):
  return render(request, 'fairshake/assessment/create.html', dict(
    model=models.Assessment._meta.verbose_name_raw,
    form=forms.AssessmentForm(),
  ))
