import logging
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
  
  def attrs(self):
    return {
      'title': self.title,
      'url': self.url,
      'description': self.description,
      'image': self.image,
      'tags': self.tags,
      'type': self.type,
    }
  
  def has_permission(self, user, perm):
    if perm in ['list', 'retrieve']:
      return True
    elif perm in ['create', 'add']:
      return user.is_authenticated or user.is_staff
    elif perm in ['modify', 'remove', 'delete']:
      if self is None:
        return user.is_authenticated
      else:
        return (self.authors and self.authors.filter(id=user.id).exists()) or user.is_staff
    else:
      logging.warning('perm %s not handled' % (perm))
      return user.is_staff

  def __str__(self):
    return '{title} ({id})'.format(id=self.id, title=self.title)

  class Meta:
    abstract = True

class Project(IdentifiableModelMixin):
  digital_objects = models.ManyToManyField('DigitalObject', blank=True, related_name='projects')
  
  class Meta:
    verbose_name = 'project'
    verbose_name_plural = 'projects'
    ordering = ['id']

  class MetaEx:
    children = [
      'digital_objects',
    ]

class DigitalObject(IdentifiableModelMixin):
  # A digital object's title is optional while its url is mandator, unlike the rest of the identifiables
  title = models.CharField(max_length=255, blank=True, null=False, default='')
  url = models.CharField(max_length=255, blank=False)

  rubrics = models.ManyToManyField('Rubric', blank=True, related_name='digital_objects')

  class Meta:
    verbose_name = 'digital_object'
    verbose_name_plural = 'digital_objects'
    ordering = ['id']

  class MetaEx:
    children = [
      'projects',
      'rubrics',
    ]

class Rubric(IdentifiableModelMixin):
  license = models.CharField(max_length=255, blank=True, null=False, default='')

  metrics = models.ManyToManyField('Metric', blank=True, related_name='rubrics')

  class Meta:
    verbose_name = 'rubric'
    verbose_name_plural = 'rubrics'
    ordering = ['id']

  class MetaEx:
    children = [
      'metrics',
      'digital_objects',
    ]

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

  class Meta:
    verbose_name = 'metric'
    verbose_name_plural = 'metrics'
    ordering = ['id']

  class MetaEx:
    children = [
      'rubrics',
    ]

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

  def has_permission(self, user, perm):
    if perm in ['list', 'retrieve']:
      return True
    elif perm in ['create', 'add']:
      return user.is_authenticated or user.is_staff
    elif perm in ['modify', 'remove', 'delete']:
      if self is None:
        return user.is_authenticated
      else:
        return (self and self.assessor == user) or user.is_staff
    else:
      logging.warning('perm %s not handled' % (perm))
      return user.is_staff

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
    ordering = ['id']

  class MetaEx:
    children = [
      'answers',
    ]

class Answer(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.ForeignKey('Assessment', on_delete=models.CASCADE, related_name='answers')
  metric = models.ForeignKey('Metric', on_delete=models.CASCADE, related_name='answers')
  answer = models.TextField(blank=True, null=False, default='')
  comment = models.TextField(blank=True, null=False, default='')
  url_comment = models.TextField(blank=True, null=False, default='')

  def value(self):
    return {
      'yes': 1,
      'yesbut': 0.75,
      'nobut': 0.25,
      'no': 0,
      '': 0,
    }.get(self.answer, 1)

  def has_permission(self, user, perm):
    return (self and self.assessment.has_permission(user, perm)) or user.is_staff

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
    ordering = ['id']

class AssessmentRequest(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.OneToOneField('Assessment', on_delete=models.CASCADE, related_name='request')
  requestor = models.ForeignKey('Author', on_delete=models.SET_NULL, related_name='+', blank=True, null=True, default='')
  timestamp = models.DateTimeField(auto_now_add=True)

  def has_permission(self, user, perm):
    if perm in ['list', 'retrieve']:
      return True
    elif perm in ['create', 'add']:
      return user.is_authenticated or user.is_staff
    elif perm in ['modify', 'remove', 'delete']:
      if self is None:
        return user.is_authenticated
      else:
        return (self and self.requestor == user) or user.is_staff
    else:
      logging.warning('perm %s not handled' % (perm))
      return user.is_staff

  def __str__(self):
    return 'Request by Requestor[{requestor}] for Assessment[{assessment}] ({id})'.format(
      id=self.id,
      assessment=self.assessment,
      requestor=self.requestor,
    )

  class Meta:
    verbose_name = 'assessment_request'
    verbose_name_plural = 'assessment_requests'
    ordering = ['id']

class Author(AbstractUser):
  def delete(self, *args, **kwargs):
    # Delete user (cascade)
    result = super().delete(*args, **kwargs)

    # Clean orphans
    # Project.objects.filter(authors=None).delete()
    # DigitalObject.objects.filter(authors=None).delete()
    # Rubric.objects.filter(authors=None).delete()
    # Metric.objects.filter(authors=None).delete()

    return result

  class Meta:
    verbose_name = 'author'
    verbose_name_plural = 'authors'
    ordering = ['id']
