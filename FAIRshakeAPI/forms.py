from django import forms
from django.forms import fields
from collections import OrderedDict
from FAIRshakeAPI import models
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField

class IdentifiableForm(forms.ModelForm):
  authors = AutoCompleteSelectMultipleField('authors', required=True, help_text=None)

  def __init__(self, *args, **kwargs):
    super(IdentifiableForm, self).__init__(*args, **kwargs)

    for child in self.Meta.model.MetaEx.children:
      self.fields[child] = AutoCompleteSelectMultipleField(
        child,
        required=False,
        help_text=None,
        initial=getattr(self.instance, child).all() if self.instance and self.instance.id else [],
      )
  
  def save(self, *args, commit=True, **kwargs):
    ''' Explicitly add children for children in the reverse direction.
    '''
    instance = super(IdentifiableForm, self).save(self, *args, **kwargs)
    if commit:
      for child in self.Meta.model.MetaEx.children:
        child_attr = getattr(instance, child)
        if child_attr.reverse:
          child_attr.clear()
          for obj in self.cleaned_data[child]:
            child_attr.add(obj)
    return instance

  class Meta:
    abstract = True

class ProjectForm(IdentifiableForm):
  class Meta:
    model = models.Project
    fields = (
      'title',
      'url',
      'description',
      'image',
      'tags',
      'type',
      'digital_objects',
      'authors',
    )

class DigitalObjectForm(IdentifiableForm):
  class Meta:
    model = models.DigitalObject
    fields = (
      'title',
      'url',
      'description',
      'image',
      'tags',
      'type',
      'rubrics',
      'authors',
    )

class RubricForm(IdentifiableForm):
  class Meta:
    model = models.Rubric
    fields = (
      'title',
      'url',
      'description',
      'image',
      'tags',
      'type',
      'license',
      'metrics',
      'authors',
    )

class MetricForm(IdentifiableForm):
  class Meta:
    model = models.Metric
    fields = (
      'title',
      'url',
      'description',
      'image',
      'tags',
      'type',
      'license',
      'rationale',
      'principle',
      'fairmetrics',
      'authors',
    )

class AssessmentForm(forms.Form):
  target = AutoCompleteSelectField('digital_objects-embedded',
    required=True,
    help_text=None,
  )
  rubric = AutoCompleteSelectField('rubrics-embedded',
    required=True,
    help_text=None,
  )
  project = AutoCompleteSelectField('projects-embedded',
    required=False,
    help_text=None,
  )

class AnswerForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(AnswerForm, self).__init__(*args, **kwargs)

    if self.instance.metric.type == 'yesno':
      self.fields = OrderedDict([
        ('answer', fields.TypedChoiceField(
          choices=[
            ('1.0', 'Yes'),
            ('0.0', 'No'),
          ],
          coerce=lambda v: float(v),
          widget=forms.RadioSelect(),
        )),
      ])
    elif self.instance.metric.type == 'yesnobut':
      self.fields = OrderedDict([
        ('answer', fields.TypedChoiceField(
          choices=[
            ('1.0', 'Yes'),
            ('0.75', 'Yes, but'),
            ('0.25', 'No, but'),
            ('0.0', 'No'),
          ],
          coerce=lambda v: float(v),
          widget=forms.RadioSelect(),
        )),
        ('url_comment', forms.CharField(
          widget=forms.Textarea(
            attrs={
              'placeholder': 'Enter URLs, if applicable and available. Separate URLs by spaces or new lines.',
              'rows': '2',
            },
          ),
          required=False,
        )),
        ('comment', forms.CharField(
          widget=forms.Textarea(
            attrs={
              'placeholder': 'Please explain or describe your answer.',
              'rows': '2',
            },
          ),
          required=False,
        )),
      ])
    elif self.instance.metric.type == 'yesnomaybe':
      self.fields = OrderedDict([
        ('answer', fields.TypedChoiceField(
          choices=[
            ('1.0', 'Yes'),
            ('0.50', 'Maybe'),
            ('0.0', 'No'),
          ],
          coerce=lambda v: float(v),
          widget=forms.RadioSelect(),
        )),
      ])
    elif self.instance.metric.type == 'url':
      self.fields = OrderedDict([
        ('url_comment', forms.CharField(
          widget=forms.Textarea(
            attrs={
              'placeholder': 'Enter URLs, if applicable and available. Separate URLs by spaces or new lines.',
              'rows': '2',
            },
          ),
          required=False,
        )),
      ])
    elif self.instance.metric.type == 'text':
      self.fields = OrderedDict([
        ('comment', forms.CharField(
          widget=forms.Textarea(
            attrs={
              'placeholder': 'Please explain or describe your answer.',
              'rows': '2',
            },
          ),
          required=False,
        )),
      ])
    else:
      raise 'Type is invalid'

  class Meta:
    model = models.Answer
    fields = (
      'answer',
    )

class AssessmentRequestForm(forms.ModelForm):
  class Meta:
    model = models.Assessment
    fields = '__all__'
