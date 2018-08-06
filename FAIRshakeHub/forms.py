from django import forms
from FAIRshakeAPI import models

class FormSets:
  def get_model(self):
    return self.model[0] if type(self.model) == tuple else self.model
  
  def get_modelform_kwargs(self):
    return self.model[1] if type(self.model) == tuple else dict()

  def get_modelform(self):
    return forms.modelform_factory(
      self.get_model(),
      **self.get_modelform_kwargs(),
    )()
  
  def get_inline_models(self):
    return [
      inline[0] if type(inline) == tuple else inline
      for inline in self.inlines
    ]
  
  def get_inline_formset_kwargs(self):
    return [
      inline[1] if type(inline) == tuple else dict()
      for inline in self.inlines
    ]

  def get_inline_formsets(self):
    return getattr(self, 'inline_formsets', [
      forms.inlineformset_factory(
        self.get_model(),
        inline,
        **kwargs,
      )
      for inline, kwargs in zip(
        self.get_inline_models(),
        self.get_inline_formset_kwargs(),
      )
    ])

class ProjectFormSets(FormSets):
  model = (models.Project, dict(
    exclude=('digital_objects', 'authors',),
  ))
  inlines = [
    (models.Project.digital_objects.through, dict(
      fields='__all__',
    )),
  ]

class DigitalObjectFormSets(FormSets):
  model = (models.DigitalObject, dict(
    exclude=('authors',),
  ))
  inlines = []

class RubricFormSets(FormSets): 
  model = (models.Rubric, dict(
    exclude=('authors',)
  ))
  inlines = [
    (models.Metric, dict(
      fields='__all__',
    )),
  ]

class MetricFormSets(FormSets): 
  model = (models.Metric, dict(
    exclude=('authors',)
  ))
  inlines = [
  ]

class AssessmentFormSets(FormSets): 
  model = (models.Assessment, dict(
    exclude=('assessor',)
  ))
  inlines = [
    (models.Answer, dict(
      fields='__all__',
    )),
  ]
