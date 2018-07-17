from django.db import models

class User(models.Model):
  user_id = models.AutoField(primary_key=True)
  username = models.TextField(blank=True, null=True)
  password = models.TextField(blank=True, null=True)
  first_name = models.TextField(blank=True, null=True)
  last_name = models.TextField(blank=True, null=True)
  role_evaluator = models.TextField(blank=True, null=True)
  role_starter = models.TextField(blank=True, null=True)
  test = models.CharField(max_length=10)

class Author(models.Model):
  id = models.AutoField(primary_key=True)
  orcid = models.TextField(blank=False, null=True)
  # user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

class IdentifiableModelMixin(models.Model):
  id = models.AutoField(primary_key=True)

  uri = models.TextField(blank=False, null=True)
  minid = models.TextField(blank=False, null=True)

  title = models.TextField(blank=False, null=False, default='null')

  description = models.TextField(blank=True, null=True, default='')
  image = models.TextField(blank=True, null=True, default='')
  tags = models.TextField(blank=True, null=True, default='')

  authors = models.ManyToManyField(Author)

  class Meta:
    abstract = True

class DigitalObject(IdentifiableModelMixin):
  url = models.URLField(blank=False, null=False, default='null')
  type = models.TextField(blank=False, null=False, default='null')

class Project(IdentifiableModelMixin):
  url = models.URLField(blank=True, null=True, default='')

  digital_objects = models.ManyToManyField(DigitalObject, related_name='projects')

class Metric(IdentifiableModelMixin):
  type = models.TextField(blank=False, null=False, default='null')
  license = models.TextField(blank=False, null=False, default='null')

  # TODO: Take all of these out of metrics
  rationale = models.URLField(blank=False, null=False, default='null')
  principle = models.URLField(blank=False, null=False, default='null')
  metrics = models.URLField(blank=True, null=True, default='')
  fairsharing = models.URLField(blank=True, null=True, default='')

class Rubric(IdentifiableModelMixin):
  type = models.TextField(blank=False, null=False, default='null')
  license = models.TextField(blank=False, null=False, default='null')

  metrics = models.ManyToManyField(Metric, related_name='rubrics')

class Assessment(models.Model):
  id = models.AutoField(primary_key=True)
  project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, related_name='+', default=0)
  rubric = models.ForeignKey(Rubric, on_delete=models.DO_NOTHING, related_name='+', default=0)
  target = models.ForeignKey(DigitalObject, on_delete=models.DO_NOTHING, related_name='+', default=0)
  methodology = models.TextField(blank=False, null=False, default='null')
  requestor = models.TextField(blank=False, null=False, default='null')
  assessor = models.TextField(blank=False, null=False, default='null')
  timestamp = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
  id = models.AutoField(primary_key=True)
  assessment = models.ForeignKey(Assessment, on_delete=models.DO_NOTHING, related_name='answers', default=0)
  metric = models.ForeignKey(Metric, on_delete=models.DO_NOTHING, related_name='+', default=0)
  answer = models.TextField(blank=False, null=False, default='null')
  comment = models.TextField(blank=True, null=True, default='')
  url_comment = models.TextField(blank=True, null=True, default='')
