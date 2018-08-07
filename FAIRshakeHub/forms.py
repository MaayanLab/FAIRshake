from django import forms
from FAIRshakeAPI import models
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

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
  class Meta:
    model = models.Assessment
    fields = '__all__'
  
  project = AutoCompleteSelectField('projects', required=True, help_text=None)
  target = AutoCompleteSelectField('digital_objects', required=True, help_text=None)
  rubric = AutoCompleteSelectField('rubrics', required=True, help_text=None)
