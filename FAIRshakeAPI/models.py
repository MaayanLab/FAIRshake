from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
  pass

class Author(models.Model):
  id = models.AutoField(primary_key=True)
  orcid = models.TextField(blank=False, null=True)
  user = models.ForeignKey('CustomUser', on_delete=models.DO_NOTHING)

class IdentifiableModelMixin(models.Model):
  id = models.AutoField(primary_key=True)

  uri = models.TextField(blank=False, null=True)
  minid = models.TextField(blank=False, null=True)

  title = models.TextField(blank=False, null=False)

  description = models.TextField(blank=True, null=True)
  image = models.TextField(blank=True, null=True)
  tags = models.TextField(blank=True, null=True)

  authors = models.ManyToManyField(Author)

  class Meta:
    abstract = True

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

  metrics = models.ManyToManyField(Metric, related_name='rubrics')

class Project(IdentifiableModelMixin):
  url = models.URLField(blank=True, null=True)

  digital_objects = models.ManyToManyField('DigitalObject', related_name='projects')

class Assessment(models.Model):
  id = models.AutoField(primary_key=True)
  project = models.ForeignKey('Project', on_delete=models.DO_NOTHING, related_name='assessments')
  rubric = models.ForeignKey('Rubric', on_delete=models.DO_NOTHING, related_name='assessments')
  target = models.ForeignKey('DigitalObject', on_delete=models.DO_NOTHING, related_name='assessments')
  methodology = models.TextField(blank=False, null=False)
  requestor = models.TextField(blank=False, null=False)
  assessor = models.TextField(blank=False, null=False)
  timestamp = models.DateTimeField(auto_now_add=True)

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

class DigitalObject(IdentifiableModelMixin):
  url = models.URLField(blank=False, null=False)
  type = models.TextField(blank=False, null=False)

  rubrics = models.ManyToManyField('Rubric', related_name='digital_objects')

class Score(DigitalObject):
  def score(self):
    score = {}
    for assessment in Assessment.objects.filter(target=self.id):
      for answer in Answer.objects.filter(assessment=assessment.id):
        score[answer.metric.id] = score.get(answer.metric, []) + [answer.value()]
    return {
      key: float(sum(value))/len(value)
      for key, value in score.items()
    }

  class Meta:
    proxy = True
