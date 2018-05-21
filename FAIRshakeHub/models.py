from django.contrib.auth.models import User
from django.db import models
from FAIRshakeRubric.models import Rubric

class Project(models.Model):
    name = models.TextField("Name")
    description = models.TextField("Description")
    img = models.ImageField("Image")

    users = models.ManyToManyField(User, related_name='projects')
    rubrics = models.ManyToManyField(Rubric, related_name='+')

class Resource(models.Model):
    name = models.TextField("Name")
    description = models.TextField("Description")
    url = models.CharField("URL", max_length=255)
    type = models.CharField("Type", max_length=255, choices=(
        ("T", "Tool"),
        # ...
    ))

    projects = models.ManyToManyField(Project, related_name='resources')
    rubrics = models.ManyToManyField(Rubric, related_name='+')
