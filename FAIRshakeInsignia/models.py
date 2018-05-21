from django.db import models
from FAIRshakeRubric.models import Rubric, Question
from FAIRshakeHub.models import Resource

class Score(models.Model):
    obj = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='+')
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name='+')

class ScoreSummary(models.Model):
    score = models.ForeignKey(Score, on_delete=models.CASCADE, related_name='summaries')
    criterion = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='+')
    average = models.FloatField("Running Average")
    timestamp = models.DateTimeField("Last Updated", auto_now=True)

    class Meta:
        unique_together = (('score', 'criterion',),)
