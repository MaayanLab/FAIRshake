from django.db import models

class API(models.Model):
    name = models.TextField("Name")
    url = models.TextField("URL")
    type = models.CharField("Type", max_length=1, choices=(
        ("E", "Evaluation provider"),
        ("R", "Rubric provider"),
        ("S", "Scoring engine"),
        ("H", "Hub"),
    ))
    updated = models.DateTimeField("Last updated", auto_now=True)

class APIDependency(models.Model):
    api = models.ForeignKey(API, on_delete=models.CASCADE, related_name="dependencies")
    dependency = models.ForeignKey(API, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = (("api", "dependency",),)
