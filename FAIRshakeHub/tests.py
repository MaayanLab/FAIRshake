from django.test import TestCase, Client
from django.urls import reverse
from FAIRshakeAPI import tests, models

class ViewsFunctionTestCase(TestCase):
  setUp = tests.setUp

  def test_index_view(self):
    response = self.anonymous_client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)

  def test_search_view(self):
    response = self.anonymous_client.get(reverse('index'), dict(q='test'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('index'), dict(q='test'))
    self.assertEqual(response.status_code, 200)

  def test_bookmarklet_view(self):
    response = self.anonymous_client.get(reverse('bookmarklet'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('bookmarklet'))
    self.assertEqual(response.status_code, 200)

  def test_chrome_extension_view(self):
    response = self.anonymous_client.get(reverse('chrome_extension'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('chrome_extension'))
    self.assertEqual(response.status_code, 200)

  def test_documentation_view(self):
    response = self.anonymous_client.get(reverse('documentation'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('documentation'))
    self.assertEqual(response.status_code, 200)

  def test_jsonschema_documentation_view(self):
    response = self.anonymous_client.get(reverse('jsonschema_documentation'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('jsonschema_documentation'))
    self.assertEqual(response.status_code, 200)

  def test_terms_of_service_view(self):
    response = self.anonymous_client.get(reverse('terms_of_service'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('terms_of_service'))
    self.assertEqual(response.status_code, 200)

  def test_contributors_and_partners_view(self):
    response = self.anonymous_client.get(reverse('contributors_and_partners'))
    self.assertEqual(response.status_code, 200)

    response = self.authenticated_client.get(reverse('contributors_and_partners'))
    self.assertEqual(response.status_code, 200)

  def test_project_stats_view(self):
    item = models.Project.objects.first()
    for plot in [
      'TablePlot',
      'RubricPieChart',
      'RubricsInProjectsOverlay',
      'DigitalObjectBarBreakdown',
      'RubricsByMetricsBreakdown',
    ]:
      response = self.anonymous_client.get(reverse('stats'), {
        'model': 'project',
        'item': item.id,
        'plot': plot,
      })
      self.assertEqual(response.status_code, 200)

  def test_project_stats_view_no_project_id(self):
    item = models.Project.objects.first()
    for plot in [
      'TablePlot',
      'RubricPieChart',
      'RubricsInProjectsOverlay',
      'DigitalObjectBarBreakdown',
      'RubricsByMetricsBreakdown',
    ]:
      response = self.anonymous_client.get(reverse('stats'), {
        'model': 'project',
        # 'item': item.id,
        'plot': plot,
      })
      self.assertEqual(response.status_code, 200)

