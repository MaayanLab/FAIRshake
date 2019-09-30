from . import models
from collections import Counter
from collections import defaultdict
from django.db.models import Count, Avg
from plotly import tools
import numpy as np
import plotly.graph_objs as go
import plotly.offline as opy

from scripts.linear_map import linear_map

def _iplot(*args, **kwargs):
  return opy.plot(*args, **kwargs, auto_open=False, output_type='div')

# Build Bar charts
def BarGraphs(data):
  data_dict=Counter(data)
  for x in [0,0.25,0.75,1]:
    if x not in  data_dict.keys():
      data_dict[x]=0
  if len(np.unique(data))>1:
    hist=[go.Bar(x=list(data_dict.keys()),y=list(data_dict.values()))]
    layout = go.Layout(xaxis=dict(title="FAIR score (0=no,0.25=nobut,0.5=maybe,0.75=yesbut,1=yes)",ticks='outside',tickvals=[0,0.25,0.5,0.75,1]),yaxis=dict(title='Responses'),width=400,height=400)
    fig = go.Figure(data=hist, layout=layout)
    yield _iplot(fig)

def RubricPieChart(assessments_with_rubric):
  values = {}
  rubrics_set = set()
  for row in assessments_with_rubric.values('rubric').order_by().annotate(count=Count('id')):
    rubric = row['rubric']
    rubrics_set.add(rubric)
    values[rubric] = row['count']
  rubrics_lookup = dict(models.Rubric.objects.filter(id__in=rubrics_set).values_list('id', 'title'))
  rubrics, values = zip(*[(rubrics_lookup[rubric], count) for rubric, count in values.items()])
  fig = [
    go.Pie(
      labels=rubrics,
      values=values,
      hoverinfo='label+value+percent',
      textinfo='percent',
    )
  ]
  yield _iplot(fig)

def RubricsInProjectsOverlay(answers_within_project):
  rubrics = models.Rubric.objects.filter(id__in=[val['rubric'] for val in answers_within_project.values('rubric').order_by().distinct()])
  values = {
    rubric.title: list(zip(*sorted([
      (answer_count['value'], models.Answer.annotate_answer(answer_count['answers__answer'], with_perc=True))
      for answer_count in answers_within_project.filter(rubric=rubric).values('answers__answer').annotate(value=Count('answers__answer')).order_by()
    ], reverse=True)))
    for rubric in rubrics
  }
  yield _iplot({
    'data': [
      go.Bar(
        x=answers,
        y=counts,
        name=rubric
      )
      for rubric, (counts, answers) in values.items()
    ],
    'layout': {
      'xaxis': {'title': 'Answer'},
      'yaxis': {'title': 'Responses'},
      'barmode': 'stack',
    },
  })

def _QuestionBarGraphs(metric_count_dict):
  hist=[go.Bar(x=list([metric_dict[x] for x in metric_count_dict.keys()]),y=list(metric_count_dict.values()))]
  layout = go.Layout(xaxis=dict(title="Metric",titlefont=dict(size=16),tickfont=dict(size=12)),yaxis=dict(title='Mean FAIR score',titlefont=dict(size=16)))
  fig = go.Figure(data=hist, layout=layout)
  yield _iplot(fig)

def QuestionBreakdown(query):
  metric_ids=iter(np.array(query4.values_list('metric',flat=True)))
  scores=iter(np.array(query4.values_list('answer',flat=True)))
  d={}
  for x,y in zip(metric_ids,scores):
    if x in d:
      d[x] = d[x] + y 
    else:
      d[x] = y
  average_score={}
  for key, value in d.items():
    average_score[key]=value/(len(scores)/9)
  return _QuestionBarGraphs(average_score)

def DigitalObjectBarBreakdown(answers_within_project):
  if answers_within_project.count() > 10000:
    yield 'Too many objects for this plot'
    return

  colors = {
    'Poor': 'rgba(255,10,10,1)',
    'Good': 'rgba(132,0,214,1)',
    'Very FAIR': 'rgba(0,0,214,1)',
  }
  level_mapper = linear_map(
    [0, 1],
    ['Poor', 'Good', 'Very FAIR'],
  )
  values = {}
  targets_set = set()
  for row in answers_within_project.values('target').order_by().annotate(Avg('answers__answer')):
    target = row['target']
    targets_set.add(target)
    score = row['answers__answer__avg']
    values[target] = score
  targets_lookup = {
    id: '{} (ID: {})'.format(title, id)
    for id, title in models.DigitalObject.objects.filter(id__in=targets_set).values_list('id', 'title')
  }

  grouped_values = {}
  for target, score in values.items():
    title = targets_lookup[target]
    annot = level_mapper(score)
    if grouped_values.get(annot) is None:
      grouped_values[annot] = []
    grouped_values[annot].append((score, target))

  for annot, vals in grouped_values.items():
    grouped_values[annot] = list(zip(*sorted(vals)))

  yield _iplot(
    go.Figure(
      data=[
        go.Bar(y=values, x=list(map(targets_lookup.get, targets)), name=annot, marker=dict(color=colors[annot]))
        for annot, (values, targets) in grouped_values.items()
      ],
      layout=go.Layout(xaxis=dict(title="Resources (n="+str(len(values))+")",showticklabels=False,titlefont=dict(size=16)),showlegend=True,yaxis=dict(title='Mean FAIR score',titlefont=dict(size=16)))
    )
  )

# Overall scores for a particular rubric, project, metric...(***Can be placed on each rubric, project, and metric page***)
# Get all scores in the database for a particular rubric, project, or metric 
# Input: Query Set (all answers), type of paramter, parameter ID
# example input query: models.Answer.objects.filter(assessment__project__id=11).all() 
def SingleQuery(querySet, PARAM, ID):
  if PARAM=="project":
    title=models.Project.objects.filter(id=ID).values_list('title', flat=True).get()
    scores=querySet.values_list('answer', flat=True)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the project:",models.Project.objects.filter(id=ID).values_list('title', flat=True).get(),"(project id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)
  if PARAM=="rubric":
    title=models.Rubric.objects.filter(id=ID).values_list('title', flat=True).get()
    scores=querySet.values_list('answer', flat=True)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the rubric:",models.Rubric.objects.filter(id=ID).values_list('title', flat=True).get(),"(rubric id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)
  if PARAM=="metric":
    title=models.Metric.objects.filter(id=ID).values_list('title', flat=True).get()
    scores=querySet.values_list('answer', flat=True)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the metric:",models.Metric.objects.filter(id=ID).values_list('title', flat=True).get(),"(metric id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)

def TablePlot(project):
  from django.template import Template, Context
  metrics = [
    metric.title
    for obj in project.digital_objects.all()
    for assessment in obj.assessments.all()
    for metric in assessment.rubric.metrics.all()
  ]
  objs = [
    obj.title
    for obj in project.digital_objects.all()
  ]
  scores = [
    [
      np.mean([
        answer.value()
        for answer in models.Answer.objects.filter(metric=metric, assessment__target=obj)
      ])
      for assessment in obj.assessments.all()
      for metric in assessment.rubric.metrics.all()
    ]
    for obj in project.digital_objects.all()
  ]
  trace = go.Heatmap(z=scores, x=metrics, y=objs)
  data = [trace]
  layout = go.Layout(xaxis=dict(title="Metrics",ticks='',
        showticklabels=False, automargin=True),yaxis=dict(title='Digital Objects',ticks='',
        showticklabels=True, automargin=True))
  fig = go.Figure(data=data, layout=layout)
  yield _iplot(fig)

def RubricsByMetricsBreakdown(answers_within_project):
  values = defaultdict(lambda: {})
  rubrics_set = set()
  metrics_set = set()
  for row in answers_within_project.values('rubric', 'answers__metric').order_by().annotate(
    Avg('answers__answer'),
  ):
    rubric = row['rubric']
    rubrics_set.add(rubric)
    metric = row['answers__metric']
    metrics_set.add(metric)
    values[rubric][metric] = row['answers__answer__avg']

  rubrics_lookup = dict(models.Rubric.objects.filter(id__in=rubrics_set).values_list('id', 'title'))
  metrics_lookup = dict(models.Metric.objects.filter(id__in=metrics_set).values_list('id', 'title'))
  fig = tools.make_subplots(rows=len(rubrics_set), cols=1, print_grid=False)
  for ind, (rubric, (metric_scores)) in enumerate(values.items()):
    metrics, scores = zip(*metric_scores.items())
    fig.append_trace(
      go.Bar(
        x=list(map(metrics_lookup.get, metrics)),
        y=scores,
        name=rubrics_lookup[rubric]
      ),
      ind+1,
      1
    )
    xaxis_num = 'xaxis%d' % (ind+1)
    fig['layout'][xaxis_num].update(showticklabels=False)
  # NOTE: this is supposed to be out of the loop
  fig['layout'][xaxis_num].update(title='Mean FAIR Score by Metric', titlefont=dict(size=16))
  yield _iplot(fig)
