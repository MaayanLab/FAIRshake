from django.db import models
from django.contrib.auth.models import AbstractUser

class IdentifiableModelMixin(models.Model):
  id = models.AutoField(primary_key=True)

  uri = models.TextField(blank=False, null=True)
  minid = models.TextField(blank=False, null=True)

  url = models.URLField(blank=False, null=True)

  title = models.TextField(blank=False, null=False)
  description = models.TextField(blank=True, null=True)
  image = models.TextField(blank=True, null=True)
  tags = models.TextField(blank=True, null=True)

  authors = models.ManyToManyField('Author', blank=True)

  class Meta:
    abstract = True

class Project(IdentifiableModelMixin):
  digital_objects = models.ManyToManyField('DigitalObject', blank=True, related_name='projects')

class DigitalObject(IdentifiableModelMixin):
  type = models.TextField(blank=False, null=False)

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

class Assessment(models.Model):
  id = models.AutoField(primary_key=True)
  project = models.ForeignKey('Project', on_delete=models.DO_NOTHING, related_name='assessments')
  target = models.ForeignKey('DigitalObject', on_delete=models.DO_NOTHING, related_name='assessments')
  rubric = models.ForeignKey('Rubric', on_delete=models.DO_NOTHING, related_name='assessments')
  methodology = models.TextField(blank=False, null=False)
  requestor = models.TextField(blank=False, null=True)
  assessor = models.TextField(blank=False, null=False)
  timestamp = models.DateTimeField(auto_now_add=True)
  # answers

class Answer(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.ForeignKey('Assessment', on_delete=models.DO_NOTHING, related_name='answers')
  metric = models.ForeignKey('Metric', on_delete=models.DO_NOTHING, related_name='answers')
  answer = models.TextField(blank=True, null=False)
  comment = models.TextField(blank=True, null=True)
  url_comment = models.TextField(blank=True, null=True)

  def value(self):
    if self.answer != '':
      if self.comment == '':
        return 0
      return 1
    return -1

class Metric(IdentifiableModelMixin):
  type = models.TextField(blank=False, null=False)
  license = models.TextField(blank=False, null=False)

  # TODO: Take all of these out of metrics
  rationale = models.URLField(blank=False, null=False)
  principle = models.URLField(blank=False, null=False)
  fairmetrics = models.URLField(blank=True, null=True)
  fairsharing = models.URLField(blank=True, null=True)

class Rubric(IdentifiableModelMixin):
  type = models.TextField(blank=False, null=False)
  license = models.TextField(blank=False, null=False)

  metrics = models.ManyToManyField('Metric', blank=True, related_name='rubrics')

class Score(DigitalObject):
  class Meta:
    proxy = True

class Author(AbstractUser):
  pass
