from django.db import models
from FAIRshakeHub.models import Resource
from FAIRshakeRubric.models import Rubric, Question

class Assessment(models.Model):
    obj = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='+')
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name='+')
    type = models.CharField("Type", max_length=1, choices=(
        ("S", "Self assessment"),
        ("T", "Test assessment"),
        ("A", "Automated assessment"),
        ("U", "User submitted assessment"),
    ))
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)

class AssessmentResult(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='+')
    answer = models.TextField("Answer (json serialized)")

    class Meta:
        unique_together = (('assessment', 'question',),)
