from django.db import models

class Rubric(models.Model):
    name = models.TextField("Name")
    description = models.TextField("Description")

class QuestionGroup(models.Model):
    rubric = models.ForeignKey(Rubric, on_delete=models.CASCADE, related_name='question_groups')
    index = models.IntegerField("Question Group Index")
    name = models.TextField("Question Group Name")
    description = models.TextField("Question Group Description")

    class Meta:
        unique_together = (('id', 'rubric',),)

class Question(models.Model):
    group = models.ForeignKey(QuestionGroup, on_delete=models.CASCADE, related_name='questions')
    index = models.IntegerField("Question Index")
    question = models.TextField("Question")
    value_type = models.TextField("Question Value Type", choices=(
        ('yesnobut', 'Yes or no but allow comment'),
        ('text', 'Single line text input'),
        ('textarea', 'Multi line text input'),
    ))

    class Meta:
        unique_together = (('id', 'group', 'index',),)
