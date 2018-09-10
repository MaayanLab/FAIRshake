from django.db import migrations, transaction

def migrate_db(forwards=None):
  def migrate(apps, schema_editor):
    Metric = apps.get_model('FAIRshakeAPI', 'Metric' if forwards else 'MetricNew')
    MetricNew = apps.get_model('FAIRshakeAPI', 'MetricNew' if forwards else 'Metric')

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

    Rubric = apps.get_model('FAIRshakeAPI', 'Rubric' if forwards else 'RubricNew')
    RubricNew = apps.get_model('FAIRshakeAPI', 'RubricNew' if forwards else 'Rubric')
    old_rubric_2_new = {}
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

    DigitalObject = apps.get_model('FAIRshakeAPI', 'DigitalObject' if forwards else 'DigitalObjectNew')
    DigitalObjectNew = apps.get_model('FAIRshakeAPI', 'DigitalObjectNew' if forwards else 'DigitalObject')
    old_obj_2_new = {}
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

    Project = apps.get_model('FAIRshakeAPI', 'Project' if forwards else 'ProjectNew')
    ProjectNew = apps.get_model('FAIRshakeAPI', 'ProjectNew' if forwards else 'Project')
    old_project_2_new = {}
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

    Assessment = apps.get_model('FAIRshakeAPI', 'Assessment' if forwards else 'AssessmentNew')
    AssessmentNew = apps.get_model('FAIRshakeAPI', 'AssessmentNew' if forwards else 'Assessment')
    old_assessment_2_new = {}
    for assessment in Assessment.objects.all():
      new_assessment = AssessmentNew.objects.create(
        project=old_project_2_new[assessment.project] if assessment.project is not None else None,
        target=old_obj_2_new[assessment.target],
        rubric=old_rubric_2_new[assessment.rubric],
        methodology=assessment.methodology,
        assessor=assessment.assessor,
      )
      old_assessment_2_new[assessment] = new_assessment

    Answer = apps.get_model('FAIRshakeAPI', 'Answer' if forwards else 'AnswerNew')
    AnswerNew = apps.get_model('FAIRshakeAPI', 'AnswerNew' if forwards else 'Answer')
    old_answer_2_new = {}
    for answer in Answer.objects.all():
      new_answer = AnswerNew.objects.create(
        assessment=old_assessment_2_new[answer.assessment],
        metric=old_metric_2_new[answer.metric],
        answer=answer.answer,
        comment=answer.comment,
        url_comment=answer.url_comment,
      )
      old_answer_2_new[answer] = new_answer

    AssessmentRequest = apps.get_model('FAIRshakeAPI', 'AssessmentRequest' if forwards else 'AssessmentRequestNew')
    AssessmentRequestNew = apps.get_model('FAIRshakeAPI', 'AssessmentRequestNew' if forwards else 'AssessmentRequest')
    old_assessment_request_2_new = {}
    for assessment_request in AssessmentRequest.objects.all():
      new_assessment_request = AssessmentRequestNew.objects.create(
        assessment=old_assessment_2_new[assessment_request.assessment],
        requestor=assessment_request.requestor,
        timestamp=assessment_request.timestamp,
      )
      old_assessment_request_2_new[assessment_request] = new_assessment_request

  return migrate

class Migration(migrations.Migration):

  dependencies = [
    ('FAIRshakeAPI', '0005_auto_20180910_1752'),
  ]

  operations = [
    migrations.RunPython(
      migrate_db(forwards=True),
      migrate_db(forwards=False),
    )
  ]
