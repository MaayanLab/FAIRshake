from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from scripts.pyswagger_wrapper import bind
from . import models

def setUp(cls, Client=Client):
  user = models.Author.objects.create(
    username='test',
    password='test',
  )
  metrics = [
    models.Metric.objects.create(
      title='yesnobut test',
      type='yesnobut',
    ),
    models.Metric.objects.create(
      title='text test',
      type='text',
    ),
    models.Metric.objects.create(
      title='url test',
      type='url',
    ),
  ]
  for metric in metrics:
    metric.authors.add(user)
  rubric = models.Rubric.objects.create(
    title='rubric test',
  )
  rubric.authors.add(user)
  for metric in metrics:
    rubric.metrics.add(metric)
  obj = models.DigitalObject.objects.create(
    url='https://fairshake.cloud/',
  )
  obj.rubrics.add(rubric)
  project = models.Project.objects.create(
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
      answer='yes',
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
        pk=models.Project.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('project-detail', kwargs=dict(
        pk=models.Project.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        pk=models.Project.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        pk=models.Project.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_digital_object_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        pk=models.DigitalObject.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        pk=models.DigitalObject.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        pk=models.DigitalObject.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        pk=models.DigitalObject.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_rubric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        pk=models.Rubric.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        pk=models.Rubric.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        pk=models.Rubric.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        pk=models.Rubric.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_metric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        pk=models.Metric.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        pk=models.Metric.objects.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        pk=models.Metric.objects.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        pk=models.Metric.objects.first().pk
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
      '/project/{pk}/'.format(pk=models.Project.objects.first().pk),
      {
        'title': 'test project improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertNotEqual(models.Project.objects.first().title, 'test project improved')

    response = self.authenticated_client.patch(
      '/project/{pk}/'.format(pk=models.Project.objects.first().pk),
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
      '/project/{pk}/'.format(pk=models.Project.objects.first().pk),
      {
        'description': 'test improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertNotEqual(models.Project.objects.first().description, 'test improved')

    response = self.authenticated_client.patch(
      '/project/{pk}/'.format(pk=models.Project.objects.first().pk),
      {
        'description': 'test improved',
      },
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(models.Project.objects.first().description, 'test improved')

  def test_project_destroy(self):
    pk = models.Project.objects.first().pk
    response = self.anonymous_client.delete(
      '/project/{pk}/'.format(pk=pk),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)
    self.assertEqual(models.Project.objects.first().pk, pk)

    response = self.authenticated_client.delete(
      '/project/{pk}/'.format(pk=pk),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 204)
    # self.assertEqual(response['Content-Type'], 'application/json', response)
    try:
      models.Project.objects.get(pk=pk)
      self.fail('Project was not deleted')
    except:
      pass
