from django import forms
from FAIRshakeAPI import models
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField
from . import fields

# TODO: build these fields with `model.children`

class ProjectForm(forms.ModelForm):
  class Meta:
    model = models.Project
    exclude = ('authors',)
  
  digital_objects = AutoCompleteSelectMultipleField('digital_objects', required=False, help_text=None)

class DigitalObjectForm(forms.ModelForm):
  class Meta:
    model = models.DigitalObject
    exclude = ('authors',)
  
  projects = AutoCompleteSelectMultipleField('projects', required=False, help_text=None)
  rubrics = AutoCompleteSelectMultipleField('rubrics', required=False, help_text=None)

class RubricForm(forms.ModelForm):
  class Meta:
    model = models.Rubric
    exclude = ('authors',)
  
  metrics = AutoCompleteSelectMultipleField('metrics', required=False, help_text=None)
  digital_objects = AutoCompleteSelectMultipleField('digital_objects', required=False, help_text=None)

class MetricForm(forms.ModelForm):
  class Meta:
    model = models.Metric
    exclude = ('authors',)
  
  rubrics = AutoCompleteSelectMultipleField('rubrics', required=False, help_text=None)

class AssessmentForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(AssessmentForm, self).__init__(*args, **kwargs)

    self.fields['project'].widget = forms.HiddenInput()
    self.fields['target'].widget = forms.HiddenInput()
    self.fields['rubric'].widget = forms.HiddenInput()

  class Meta:
    model = models.Assessment
    exclude = (
      'assessor',
      'methodology',
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
