from django import forms

answer_fields = {
  'yesnobut': forms.ChoiceField(
    choices=[
      ('yes', 'Yes'),
      ('yesbut', 'Yes, but'),
      ('no', 'No'),
      ('nobut', 'No, but'),
    ],
    widget=forms.RadioSelect(),
  ),
  'yesnomaybe': forms.ChoiceField(
    choices=[
      ('yes', 'Yes'),
      ('no', 'No'),
      ('maybe', 'Maybe'),
    ],
    widget=forms.RadioSelect(),
  ),
  'url': forms.URLField(),
  'text': forms.CharField(
    widget=forms.Textarea(
      attrs={
        'placeholder': 'Insert your answer.',
        'rows': '3',
      },
    ),
  ),
}
