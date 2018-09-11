import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAIRshake.settings")
import django
django.setup()

from FAIRshakeAPI import models

from scripts import db
sess = db.get_db_session('TODO_DB_URI')

me = models.Author.objects.get(id=1)

old_t_to_new_t = {
  'Tool': 'tool',
  'Dataset': 'data',
  'Repository': 'repo',
}

# Digital Objects
old_d_to_new_d = {}
for d in sess.query(db.Resource):
  new_d = models.DigitalObject(
    title=d.resource_name,
    url=d.url,
    description=d.description,
    type=old_t_to_new_t[d.resource_type],
    tags='DCPPC',
  )
  new_d.save()
  new_d.authors.add(me)
  old_d_to_new_d[d.resource_id] = new_d.id

type_to_rubric = {
  'tool': models.Rubric.objects.get(id=7),
  'data': models.Rubric.objects.get(id=8),
  'repo': models.Rubric.objects.get(id=9),
}

# Resource type to rubric
for d in old_d_to_new_d.values():
  obj = models.DigitalObject.objects.get(id=d)
  obj.rubrics.add(type_to_rubric[obj.type])

# Evaluation to Assessment
assessments = {}
for e in sess.query(db.Evaluation):
  assess = assessments.get(
    (e.user_id, e.resource_id,),
    models.Assessment(
      target=models.DigitalObject.objects.get(id=old_d_to_new_d[e.resource_id]),
      rubric=type_to_rubric[
        models.DigitalObject.objects.get(id=old_d_to_new_d[e.resource_id]).type
      ],
      methodology='test',
      assessor=me,
    )
  )
  assessments[(e.user_id, e.resource_id,)] = assess
  assess.save()
  answer = models.Answer(
    assessment=assess,
    metric=models.Metric.objects.get(id=q_to_m[e.q_id]),
    answer=e.answer or '',
    comment=e.comment or '',
    url_comment=e.url_comment or '',
  )
  answer.save()
