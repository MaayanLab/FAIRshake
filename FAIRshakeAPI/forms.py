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

  def clean_slug(self):
    slug = self.cleaned_data.get('slug')
    try:
      if self.Meta.model.objects.current.get(slug=slug) != self.instance:
        raise forms.ValidationError(
          'Slug was already taken, please try something different.'
        )
    except self.Meta.model.DoesNotExist:
      pass
    return slug

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
      'slug',
      'digital_objects',
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
      'slug',
      'rubrics',
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
      'slug',
      'license',
      'metrics',
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
      'slug',
      'license',
      'rationale',
      'principle',
      'fairmetrics',
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
