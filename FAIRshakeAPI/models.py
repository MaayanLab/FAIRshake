from django.db import models
from django.contrib.auth.models import AbstractUser
from collections import OrderedDict

class IdentifiableModelMixin(models.Model):
  id = models.AutoField(primary_key=True)

  title = models.CharField(max_length=255, blank=False)
  url = models.CharField(max_length=255, blank=True, null=False, default='')
  description = models.TextField(blank=True, null=False, default='')
  image = models.CharField(max_length=255, blank=True, null=False, default='')
  tags = models.CharField(max_length=255, blank=True, null=False, default='')

  type = models.CharField(max_length=16, blank=True, null=False, default='', choices=(
    ('', 'Other'),
    ('any', 'Any Digital Object'),
    ('data', 'Dataset'),
    ('repo', 'Repository'),
    ('test', 'Test Object'),
    ('tool', 'Tool'),
  ))

  authors = models.ManyToManyField('Author', blank=True)

  def tags_as_list(self):
    return self.tags.split()
  
  def model_name(self):
    return self._meta.verbose_name_raw

  def __str__(self):
    return '{title} ({id})'.format(id=self.id, title=self.title)

  class Meta:
    abstract = True

class Project(IdentifiableModelMixin):
  digital_objects = models.ManyToManyField('DigitalObject', blank=True, related_name='projects')

  def children(self):
    return OrderedDict([
      ('digital_object', self.digital_objects.all()),
    ])
  
  class Meta:
    verbose_name = 'project'
    verbose_name_plural = 'projects'

class DigitalObject(IdentifiableModelMixin):
  # A digital object's title is optional while its url is mandator, unlike the rest of the identifiables
  title = models.CharField(max_length=255, blank=True, null=False, default='')
  url = models.CharField(max_length=255, blank=False)

  rubrics = models.ManyToManyField('Rubric', blank=True, related_name='digital_objects')

  def score(self, projects=None, rubrics=None):
    '''
    Generate aggregate scores on a per-rubric and per-metric basis.
    '''
    scores = {}

    for assessment in Assessment.objects.filter(
      target=self.id,
      rubric__in=rubrics,
      project__in=projects,
    ):
      if scores.get(assessment.rubric.id) is None:
        scores[assessment.rubric.id] = {}
      for answer in Answer.objects.filter(
        assessment=assessment.id,
      ):
        if scores[assessment.rubric.id].get(answer.metric.id) is None:
          scores[assessment.rubric.id][answer.metric.id] = []
        scores[assessment.rubric.id][answer.metric.id].append(answer.value())

    return {
      rubric: {
        metric: sum(value)/len(value)
        for metric, value in score.items()
      }
      for rubric, score in scores.items()
    }

  def children(self):
    return OrderedDict([
      ('project', self.projects.all()),
      ('rubric', self.rubrics.all()),
    ])

  class Meta:
    verbose_name = 'digital_object'
    verbose_name_plural = 'digital_objects'

class AssessmentRequest(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.OneToOneField('Assessment', on_delete=models.CASCADE, related_name='request')
  requestor = models.ForeignKey('Author', on_delete=models.SET_NULL, related_name='+', blank=True, null=True, default='')
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return 'Request by Requestor[{requestor}] for Assessment[{assessment}] ({id})'.format(
      id=self.id,
      assessment=self.assessment,
      requestor=self.requestor,
    )

  class Meta:
    verbose_name = 'assessment_request'
    verbose_name_plural = 'assessment_requests'

class Assessment(models.Model):
  id = models.AutoField(primary_key=True)
  project = models.ForeignKey('Project', on_delete=models.SET_NULL, blank=True, null=True, related_name='assessments')
  target = models.ForeignKey('DigitalObject', on_delete=models.CASCADE, related_name='assessments')
  rubric = models.ForeignKey('Rubric', on_delete=models.CASCADE, related_name='assessments')
  methodology = models.TextField(max_length=16, blank=True, choices=(
    ('self', 'Digital Object Creator Assessment'),
    ('user', 'Independent User Assessment'),
    ('auto', 'Automatic Assessment'),
    ('test', 'Test Assessment'),
  ))
  assessor = models.ForeignKey('Author', on_delete=models.SET_NULL, related_name='+', blank=True, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return '{methodology} assessment on Target[{target}] for Project[{project}] with Rubric[{rubric}] ({id})'.format(
      id=self.id,
      project=self.project,
      target=self.target,
      rubric=self.rubric,
      methodology=self.methodology
    )

  class Meta:
    verbose_name = 'assessment'
    verbose_name_plural = 'assessments'

class Answer(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='answers')
  metric = models.ForeignKey('Metric', on_delete=models.CASCADE, related_name='answers')
  answer = models.TextField(blank=True, null=False, default='')
  comment = models.TextField(blank=True, null=False, default='')
  url_comment = models.TextField(blank=True, null=False, default='')

  def value(self):
    if self.answer != '' and self.answer != 'no':
      return 1
    elif self.comment != '' or self.url_comment != '':
      return 0
    else:
      return -1

  def __str__(self):
    return 'Answer to Metric[{metric}] for assessment[{assessment}]: {answer} ({id})'.format(
      id=self.id,
      assessment=self.assessment,
      metric=self.metric,
      answer=self.answer,
    )

  class Meta:
    verbose_name = 'answer'
    verbose_name_plural = 'answers'

class Metric(IdentifiableModelMixin):
  type = models.CharField(max_length=16, blank=True, null=False, default='yesnobut', choices=(
    ('yesnobut', 'Yes no or but question'),
    ('text', 'Simple textbox input'),
    ('url', 'A url input'),
  ))

  license = models.CharField(max_length=255, blank=True, null=False, default='')

  rationale = models.TextField(blank=True, null=False, default='')
  principle = models.CharField(max_length=16, blank=True, null=False, default='', choices=(
    ('F', 'Findability',),
    ('A', 'Accessibility',),
    ('I', 'Interoperability',),
    ('R', 'Reusability',),
  ))
  fairmetrics = models.CharField(max_length=255, blank=True, null=False, default='')
  fairsharing = models.CharField(max_length=255, blank=True, null=False, default='')

  def children(self):
    return {
      'rubric': self.rubrics.all(),
    }

  class Meta:
    verbose_name = 'metric'
    verbose_name_plural = 'metrics'

class Rubric(IdentifiableModelMixin):
  license = models.CharField(max_length=255, blank=True, null=False, default='')

  metrics = models.ManyToManyField('Metric', blank=True, related_name='rubrics')

  def children(self):
    return OrderedDict([
      ('metric', self.metrics.all()),
      ('digital_object', self.digital_objects.all()),
    ])

  class Meta:
    verbose_name = 'rubric'
    verbose_name_plural = 'rubrics'

class Author(AbstractUser):
  class Meta:
    verbose_name = 'author'
    verbose_name_plural = 'authors'
