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
  if request.method == 'POST':
    form = forms.ProjectForm(request.POST)
    instance = form.save()
    instance.authors.add(request.user)
    return redirect(
      models.Project._meta.verbose_name_raw+'-detail',
      pk=instance.id
    )
  elif request.method == 'GET':
    return render(request, 'fairshake/project/create.html', dict(
      model=models.Project._meta.verbose_name_raw,
      form=forms.ProjectForm(request.GET),
    ))

@login_required
def rubric_create(request):
  if request.method == 'POST':
    form = forms.RubricForm(request.POST)
    instance = form.save()
    instance.authors.add(request.user)
    return redirect(
      models.Rubric._meta.verbose_name_raw+'-detail',
      pk=instance.id
    )
  elif request.method == 'GET':
    return render(request, 'fairshake/rubric/create.html', dict(
      model=models.Rubric._meta.verbose_name_raw,
      form=forms.RubricForm(request.GET),
    ))

@login_required
def digital_object_create(request):
  if request.method == 'POST':
    form = forms.DigitalObjectForm(request.POST)
    instance = form.save()
    instance.authors.add(request.user)
    return redirect(
      models.DigitalObject._meta.verbose_name_raw+'-detail',
      pk=instance.id
    )
  elif request.method == 'GET':
    return render(request, 'fairshake/digitalobject/create.html', dict(
      model=models.DigitalObject._meta.verbose_name_raw,
      form=forms.DigitalObjectForm(request.GET),
    ))

@login_required
def metric_create(request):
  if request.method == 'POST':
    form = forms.MetricForm(request.POST)
    instance = form.save()
    instance.authors.add(request.user)
    return redirect(
      models.Metric._meta.verbose_name_raw+'-detail',
      pk=instance.id
    )
  elif request.method == 'GET':
    return render(request, 'fairshake/metric/create.html', dict(
      model=models.Metric._meta.verbose_name_raw,
      form=forms.MetricForm(request.GET),
    ))

@login_required
def assessment_create(request):
  if request.method == 'POST':
    form = forms.AssessmentForm(request.POST)
    instance = form.save()
    instance.authors.add(request.user)
    return redirect(
      models.Assessment._meta.verbose_name_raw+'-detail',
      pk=instance.id
    )
  elif request.method == 'GET':
    return render(request, 'fairshake/assessment/create.html', dict(
      model=models.Assessment._meta.verbose_name_raw,
      form=forms.AssessmentForm(request.GET),
    ))
