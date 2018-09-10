from django.db import migrations, transaction

def migrate_db(forwards=None):
  def migrate(apps, schema_editor):
    if forwards:
      Metric = apps.get_model('FAIRshakeAPI', 'Metric')
      MetricNew = apps.get_model('FAIRshakeAPI', 'MetricNew')
    else:
      Metric = apps.get_model('FAIRshakeAPI', 'MetricNew')
      MetricNew = apps.get_model('FAIRshakeAPI', 'Metric')

    old_metric_2_new = {}
    for metric in Metric.objects.all():
      new_metric = MetricNew.objects.create(
        title=metric.title,
        url=metric.url,
        description=metric.description,
        image=metric.image,
        tags=metric.tags,
        type=metric.type,
        license=metric.license,
        rationale=metric.rationale,
        principle=metric.principle,
        fairmetrics=metric.fairmetrics,
      )
      for author in metric.authors.all():
        new_metric.authors.add(author)
      old_metric_2_new[metric] = new_metric

    old_rubric_2_new = {}
    Rubric = apps.get_model('FAIRshakeAPI', 'Rubric')
    RubricNew = apps.get_model('FAIRshakeAPI', 'RubricNew')
    for rubric in Rubric.objects.all():
      new_rubric = RubricNew.objects.create(
        title=rubric.title,
        url=rubric.url,
        description=rubric.description,
        image=rubric.image,
        tags=rubric.tags,
        type=rubric.type,
        license=rubric.license,
      )
      for author in rubric.authors.all():
        new_rubric.authors.add(author)
      for metric in rubric.metrics.all():
        new_rubric.metrics.add(old_metric_2_new[metric])
      old_rubric_2_new[rubric] = new_rubric

    old_obj_2_new = {}
    DigitalObject = apps.get_model('FAIRshakeAPI', 'DigitalObject')
    DigitalObjectNew = apps.get_model('FAIRshakeAPI', 'DigitalObjectNew')
    for obj in DigitalObject.objects.all():
      new_obj = DigitalObjectNew.objects.create(
        title=obj.title,
        url=obj.url,
        description=obj.description,
        image=obj.image,
        tags=obj.tags,
        type=obj.type,
        fairsharing=obj.fairsharing,
      )
      for author in obj.authors.all():
        new_obj.authors.add(author)
      for rubric in obj.rubrics.all():
        new_obj.rubrics.add(old_rubric_2_new[rubric])
      old_obj_2_new[obj] = new_obj

    old_project_2_new = {}
    Project = apps.get_model('FAIRshakeAPI', 'Project')
    ProjectNew = apps.get_model('FAIRshakeAPI', 'ProjectNew')
    for project in Project.objects.all():
      new_project = ProjectNew.objects.create(
        title=project.title,
        url=project.url,
        description=project.description,
        image=project.image,
        tags=project.tags,
        type=project.type,
      )
      for author in project.authors.all():
        new_project.authors.add(author)
      for obj in project.digital_objects.all():
        new_project.digital_objects.add(old_obj_2_new[obj])
      old_project_2_new[project] = new_project

    old_assessment_2_new = {}
    Assessment = apps.get_model('FAIRshakeAPI', 'Assessment')
    AssessmentNew = apps.get_model('FAIRshakeAPI', 'AssessmentNew')
    for assessment in Assessment.objects.all():
      new_assessment = AssessmentNew.objects.create(
        project=old_project_2_new[assessment.project],
        target=old_obj_2_new[assessment.target],
        rubric=old_rubric_2_new[assessment.rubric],
        methodology=assessment.methodology,
        assessor=assessment.assessor,
      )
      old_assessment_2_new[assessment] = new_assessment

    old_answer_2_new = {}
    Answer = apps.get_model('FAIRshakeAPI', 'Answer')
    AnswerNew = apps.get_model('FAIRshakeAPI', 'AnswerNew')
    for answer in Answer.objects.all():
      new_answer = AnswerNew.objects.create(
        assessment=old_assessment_2_new[answer.assessment],
        metric=old_metric_2_new[answer.metric],
        answer=answer.answer,
        comment=answer.comment,
        url_comment=answer.url_comment,
      )
      old_answer_2_new[answer] = new_answer

  return migrate

class Migration(migrations.Migration):

  dependencies = [
    ('FAIRshakeAPI', '0005_auto_20180910_1449'),
  ]

  operations = [
    migrations.RunPython(
      migrate_db(forwards=True),
      migrate_db(forwards=False),
    )
  ]
