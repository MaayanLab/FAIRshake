import json
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from pyswaggerclient.util import bind
from . import models
from unittest import skip

def setUp(cls, Client=Client):
  user = models.Author.objects.create(
    username='test',
    password='test',
  )
  metrics = [
    models.Metric.objects.create(
      slug='1',
      title='yesnobut test',
      type='yesnobut',
    ),
    models.Metric.objects.create(
      slug='2',
      title='text test',
      type='text',
    ),
    models.Metric.objects.create(
      slug='3',
      title='url test',
      type='url',
    ),
  ]
  for metric in metrics:
    metric.authors.add(user)
  rubric = models.Rubric.objects.create(
    slug='1',
    title='rubric test',
  )
  rubric.authors.add(user)
  for metric in metrics:
    rubric.metrics.add(metric)
  obj = models.DigitalObject.objects.create(
    slug='1',
    title='digital object test',
    url='https://fairshake.cloud/',
  )
  obj.rubrics.add(rubric)
  project = models.Project.objects.create(
    slug='1',
    title='project test',
  )
  project.authors.add(user)
  project.digital_objects.add(obj)
  assessment = models.Assessment.objects.create(
    project=project,
    target=obj,
    rubric=rubric,
    assessor=user,
  )
  for metric in metrics:
    models.Answer.objects.create(
      assessment=assessment,
      metric=metric,
      answer=1.0,
    )
  obj2 = models.DigitalObject.objects.create(
    slug='2',
    title='test object create',
    url='https://fairshake.cloud'
  )
  cls.anonymous_client = Client()
  cls.authenticated_client = Client()
  cls.authenticated_client.force_login(user)

class ViewsFunctionTestCase(TestCase):
  setUp = setUp

  def test_project_viewset_list(self):
    response = self.anonymous_client.get(reverse('project-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('project-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('project-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('project-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_digital_object_viewset_list(self):
    response = self.anonymous_client.get(reverse('digital_object-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('digital_object-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('digital_object-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('digital_object-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_rubric_viewset_list(self):
    response = self.anonymous_client.get(reverse('rubric-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('rubric-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('rubric-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('rubric-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_metric_viewset_list(self):
    response = self.anonymous_client.get(reverse('metric-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('metric-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('metric-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('metric-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_assessment_viewset_list(self):
    response = self.anonymous_client.get(reverse('assessment-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('assessment-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('assessment-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 401, 'Permission denied expected')
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('assessment-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_score_viewset_list(self):
    response = self.anonymous_client.get(reverse('score-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(reverse('score-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_project_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_digital_object_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_rubric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_metric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_assessment_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401, 'Permission denied expected')
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_assessment_prepare_all_params(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_no_params(self):
    response = self.anonymous_client.get(
      '{baseUrl}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_target(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_target_rubric(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_target_project(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        target=models.DigitalObject.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_rubric(self):
    response = self.anonymous_client.get(
      '{baseUrl}?rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_rubric_project(self):
    response = self.anonymous_client.get(
      '{baseUrl}?rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_prepare_project(self):
    response = self.anonymous_client.get(
      '{baseUrl}?project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?project={project}'.format(
        baseUrl=reverse(
          'assessment-prepare'
        ), 
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)


  def test_assessment_perform_all_params(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)
  
  def test_assessment_perform_target_only(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_target_rubric(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_target_project(self):
    response = self.anonymous_client.get(
      '{baseUrl}?target={target}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?target={target}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        target=models.DigitalObject.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_rubric(self):
    response = self.anonymous_client.get(
      '{baseUrl}?rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?rubric={rubric}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        rubric=models.Rubric.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_rubric_project(self):
    response = self.anonymous_client.get(
      '{baseUrl}?rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?rubric={rubric}&project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        rubric=models.Rubric.objects.first().slug,
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_project_only(self):
    response = self.anonymous_client.get(
      '{baseUrl}?project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}?project={project}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
        project=models.Project.objects.first().slug,
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_assessment_perform_no_params(self):
    response = self.anonymous_client.get(
      '{baseUrl}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      '{baseUrl}'.format(
        baseUrl=reverse(
          'assessment-perform'
        ), 
      ),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)


  def test_add_rubric(self):
    response = self.anonymous_client.get(
      reverse('rubric-add'),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.post(
      reverse('rubric-add'),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)


  def test_stats_project_view(self):
    # stats
    response = self.anonymous_client.get(
      reverse('project-stats', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('project-stats', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_modify_project_view(self):
    response = self.authenticated_client.get(
      reverse('project-modify', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.post(
      reverse('project-modify', kwargs=dict(
        slug=models.Project.objects.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

  def test_digital_object_remove(self):
    slug = models.Project.objects.first().slug

    response = self.anonymous_client.get(
      reverse('project-remove', kwargs=dict(
        slug=slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302, 'Login redirect expected')
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)
    self.assertEqual(models.DigitalObject.objects.first().slug, slug)

    response = self.authenticated_client.get(
      reverse('project-remove', kwargs=dict(
        slug=slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)
    try:
      models.Project.objects.get(slug=slug)
      self.fail('Project was not deleted')
    except:
      pass


class InteractFunctionTestCase(TestCase):
  setUp = bind(setUp, Client=APIClient)

  def test_project_create(self):
    response = self.anonymous_client.post(
      '/project/',
      {
        'title': 'test project 2',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    try:
      models.Project.objects.get(title='test project 2')
      self.fail('Project was created')
    except:
      pass

    response = self.authenticated_client.post(
      '/project/',
      {
        'slug': '2',
        'title': 'test project 2',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    try:
      models.Project.objects.get(title='test project 2')
    except:
      self.fail('Project was not created')

  def test_project_update(self):
    response = self.anonymous_client.put(
      '/project/{slug}/'.format(slug=models.Project.objects.first().slug),
      {
        'title': 'test project improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertNotEqual(models.Project.objects.first().title, 'test project improved')

    response = self.authenticated_client.patch(
      '/project/{slug}/'.format(slug=models.Project.objects.first().slug),
      {
        'title': 'test project improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(models.Project.objects.first().title, 'test project improved')

  def test_project_partial_update(self):
    response = self.anonymous_client.patch(
      '/project/{slug}/'.format(slug=models.Project.objects.first().slug),
      {
        'description': 'test improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertNotEqual(models.Project.objects.first().description, 'test improved')

    response = self.authenticated_client.patch(
      '/project/{slug}/'.format(slug=models.Project.objects.first().slug),
      {
        'description': 'test improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(models.Project.objects.first().description, 'test improved')

  def test_project_destroy(self):
    slug = models.Project.objects.first().slug
    response = self.anonymous_client.delete(
      '/project/{slug}/'.format(slug=slug),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(models.Project.objects.first().slug, slug)

    response = self.authenticated_client.delete(
      '/project/{slug}/'.format(slug=slug),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 204)
    # self.assertEqual(response['Content-Type'], 'application/json', response)
    try:
      models.Project.objects.get(slug=slug)
      self.fail('Project was not deleted')
    except:
      pass
  
  ################################
  def test_assessment_create(self):
    project=models.Project.objects.first()
    rubric=models.Rubric.objects.first()
    target=models.DigitalObject.objects.last()
    author=models.Author.objects.first()

    response = self.anonymous_client.post(
      '/assessment/',
      json.dumps({
        'project': project.slug,
        'target': target.slug,
        'rubric': rubric.slug,
        'answers': json.dumps([
          {
            'metric': 1,
            'answer': 'no',
          },
          {
            'metric': 2,
            'answer': 'no',
          },
          {
            'metric': 3,
            'answer': 'no',
          },
        ]),
      }),
      content_type='application/json',
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    try:
      models.Assessment.objects.get(project=project, rubric=rubric, target=target)
      self.fail('Found assessment')
    except:
      pass

    response = self.authenticated_client.post(
      '/assessment/',
      json.dumps({
        'project': project.slug,
        'target': target.slug,
        'rubric': rubric.slug,
        'answers': [
          {
            'metric': 1,
            'answer': 0.0,
          },
          {
            'metric': 2,
            'answer': 0.0,
          },
          {
            'metric': 3,
            'answer': 0.0,
          },
        ],
      }),
      content_type='application/json',
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 201)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(
      models.Assessment.objects.get(assessor=author, project=project, rubric=rubric, target=target).answers.count(),
      3
    )
