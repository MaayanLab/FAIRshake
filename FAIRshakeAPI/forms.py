from django import forms
from FAIRshakeAPI import models
from ajax_select.fields import AutoCompleteSelectMultipleField
from . import fields

class IdentifiableForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(IdentifiableForm, self).__init__(*args, **kwargs)

    for child in self.Meta.model.MetaEx.children:
      self.fields[child] = AutoCompleteSelectMultipleField(
        child,
        required=False,
        help_text=None,
      )

  class Meta:
    abstract = True

class ProjectForm(IdentifiableForm):
  class Meta:
    model = models.Project
    exclude = ('authors',)

class DigitalObjectForm(IdentifiableForm):
  class Meta:
    model = models.DigitalObject
    exclude = ('authors',)

class RubricForm(IdentifiableForm):
  class Meta:
    model = models.Rubric
    exclude = ('authors',)

class MetricForm(IdentifiableForm):
  class Meta:
    model = models.Metric
    exclude = ('authors',)

class AssessmentForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(AssessmentForm, self).__init__(*args, **kwargs)

    self.fields['target'].widget = forms.HiddenInput()
    self.fields['rubric'].widget = forms.HiddenInput()
    self.fields['project'].widget = forms.HiddenInput()

  class Meta:
    model = models.Assessment
    fields = (
      'target',
      'rubric',
      'project',
    )

class AnswerForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(AnswerForm, self).__init__(*args, **kwargs)

    answer_field = fields.answer_fields.get(self.instance.metric.type, None)
    if answer_field is not None:
      self.fields['answer'] = answer_field
  
  answer = forms.CharField()

  comment = forms.CharField(
    widget=forms.Textarea(
      attrs={
        'placeholder': 'Please explain or describe your answer.',
        'rows': '2',
      },
    ),
    required=False,
  )

  url_comment = forms.CharField(
    widget=forms.Textarea(
      attrs={
        'placeholder': 'Enter URLs, if applicable and available. Separate URLs by spaces or new lines.',
        'rows': '2',
      },
    ),
    required=False,
  )

  class Meta:
    model = models.Answer
    exclude = (
      'assessment',
      'metric',
    )

class AssessmentRequestForm(forms.ModelForm):
  class Meta:
    model = models.Assessment
    fields = '__all__'
