from django.db import migrations


def forwards_func(apps, schema_editor):
  DigitalObject = apps.get_model("FAIRshakeAPI", "DigitalObject")
  Metric = apps.get_model("FAIRshakeAPI", "Metric")
  Project = apps.get_model("FAIRshakeAPI", "Project")
  Rubric = apps.get_model("FAIRshakeAPI", "Rubric")
  Url = apps.get_model("FAIRshakeAPI", "Url")
  models = [DigitalObject, Metric, Project, Rubric]
  for model in models:
    for entity in model.objects.all():
      url_list = [
        url
        for url in map(str.strip, re.split(r'[\n ]+', model.raw_url))
        if url
      ]
      for url in url_list:
        entity.url.add(Url.from_url(url))

def reverse_func(apps, schema_editor):
  DigitalObject = apps.get_model("FAIRshakeAPI", "DigitalObject")
  Metric = apps.get_model("FAIRshakeAPI", "Metric")
  Project = apps.get_model("FAIRshakeAPI", "Project")
  Rubric = apps.get_model("FAIRshakeAPI", "Rubric")
  Url = apps.get_model("FAIRshakeAPI", "Url")
  models = [DigitalObject, Metric, Project, Rubric]
  for model in models:
    for entity in model.objects.all():
      entity.url_raw = '\n'.join(
        url.to_url()
        for url in entity.url.all()
      )
      entity.save()

class Migration(migrations.Migration):

  dependencies = [
    ('FAIRshakeAPI', '0015_auto_20200929_1755'),
  ]

  operations = [
    migrations.RunPython(forwards_func, reverse_func),
  ]
