from django.test import TestCase, Client
from django.urls import reverse
from . import models

class ViewsFunctionTestCase(TestCase):
  def setUp(self):
    user = models.Author.objects.create(
      username='test',
      password='test',
    )
    metrics = [
      models.Metric.objects.create(
        title='yesnobut test',
        type='yesnobut',
        slug='yesnobut',
      ),
      models.Metric.objects.create(
        title='text test',
        type='text',
        slug='text',
      ),
      models.Metric.objects.create(
        title='url test',
        type='url',
        slug='url',
      ),
    ]
    for metric in metrics:
      metric.authors.add(user)
    rubric = models.Rubric.objects.create(
      title='rubric test',
      slug='test',
    )
    rubric.authors.add(user)
    for metric in metrics:
      rubric.metrics.add(metric)
    obj = models.DigitalObject.objects.create(
      url='https://fairshake.cloud/',
      slug='fairshake',
    )
    obj.rubrics.add(rubric)
    project = models.Project.objects.create(
      title='project test',
      slug='test',
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

    self.anonymous_client = Client()
    self.authenticated_client = Client()
    self.authenticated_client.force_login(user)

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
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(reverse('assessment-list'), HTTP_ACCEPT='text/html')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(reverse('assessment-list'), HTTP_ACCEPT='application/json')
    self.assertEqual(response.status_code, 401)
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
        slug=models.Project.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('project-detail', kwargs=dict(
        slug=models.Project.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_digital_object_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('digital_object-detail', kwargs=dict(
        slug=models.DigitalObject.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_rubric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('rubric-detail', kwargs=dict(
        slug=models.Rubric.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_metric_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.current.first().slug
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('metric-detail', kwargs=dict(
        slug=models.Metric.objects.current.first().slug
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)

  def test_assessment_viewset_detail(self):
    response = self.anonymous_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.current.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.anonymous_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.current.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 401)
    self.assertEqual(response['Content-Type'], 'application/json', response)

    response = self.authenticated_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.current.first().pk
      )),
      HTTP_ACCEPT='text/html',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8', response)

    response = self.authenticated_client.get(
      reverse('assessment-detail', kwargs=dict(
        pk=models.Assessment.objects.current.first().pk
      )),
      HTTP_ACCEPT='application/json',
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response['Content-Type'], 'application/json', response)
