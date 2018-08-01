#!/bin/env python manage.py shell
from FAIRshakeAPI import models

import db
sess = db.get_db_session('TODO_DB_URI')

me = models.Author.objects.get(id=1)

old_t_to_new_t = {
  'Tool': 'tool',
  'Dataset': 'data',
  'Repository': 'repo',
}

# Projects
old_p_to_new_p = {}
for p in sess.query(db.Project):
  new_p = models.Project(
    title=p.project_name,
    description=p.project_description,
    image=p.project_img,
    type='test',
    tags='test',
  )
  new_p.save()
  new_p.authors.add(me)
  old_p_to_new_p[p.project_id] = new_p.id

# Digital Objects
old_d_to_new_d = {}
for d in sess.query(db.Resource):
  new_d = models.DigitalObject(
    title=d.resource_name,
    url=d.url,
    description=d.description,
    type=old_t_to_new_t[d.resource_type],
    tags='test',
  )
  new_d.save()
  new_d.authors.add(me)
  old_d_to_new_d[d.resource_id] = new_d.id

# Digital Objects in Projects
for rip in sess.query(db.ResourceInProject):
  models.Project.objects.get(
    id=old_p_to_new_p[rip.project_id]
  ).digital_objects.add(old_d_to_new_d[rip.resource_id])

# Question to Rubric and Metrics
tool_rubric = models.Rubric(
  title='The FAIRshake tool rubric.',
  description='An initial rubric for asking quesitons about tools.',
  tags='test fairshake',
  type='tool',
  license='MIT',
)
tool_rubric.save()
tool_rubric.authors.add(me)
dataset_rubric = models.Rubric(
  title='The FAIRshake dataset rubric.',
  description='An initial dataset for asking quesitons about datasets.',
  tags='test fairshake',
  type='data',
  license='MIT',
)
dataset_rubric.save()
dataset_rubric.authors.add(me)
repo_rubric = models.Rubric(
  title='The FAIRshake repository rubric.',
  description='An initial rubric for asking quesitons about repositories.',
  tags='test fairshake',
  type='repo',
  license='MIT',
)
repo_rubric.save()
repo_rubric.authors.add(me)

type_to_rubric={
  'tool': tool_rubric,
  'data': dataset_rubric,
  'repo': repo_rubric,
}

def q_to_principle(q):
  if q.F == 'F':
    return 'F'
  if q.A == 'A':
    return 'A'
  if q.I == 'I':
    return 'I'
  if q.R == 'R':
    return 'R'
  return ''

q_to_m = {}

for q in sess.query(db.Question):
  r = type_to_rubric[old_t_to_new_t[q.res_type]]
  m = models.Metric(
    title=q.content,
    type='yesnobut',
    tags='test fairshake',
    license='MIT',
    principle=q_to_principle(q),
  )
  m.save()
  m.authors.add(me)
  r.metrics.add(m)
  q_to_m[q.q_id] = m.id


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
      project=models.Project.objects.get(id=old_p_to_new_p[e.project_id]),
      target=models.DigitalObject.objects.get(id=old_d_to_new_d[e.resource_id]),
      rubric=type_to_rubric[
        models.DigitalObject.objects.get(id=old_d_to_new_d[e.resource_id]).type
      ],
      methodology='test',
      assessor=me,
      requestor=me,
    )
  )
  assess.save()
  answer = models.Answer(
    assessment=assess,
    metric=models.Metric.objects.get(id=q_to_m[e.q_id]),
    answer=e.answer or '',
    comment=e.comment or '',
    url_comment=e.url_comment or '',
  )
  answer.save()
