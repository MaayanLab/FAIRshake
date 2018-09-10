from . import models
import plotly.offline as opy
import plotly.graph_objs as go
from collections import Counter
import numpy as np

# Dictionary converts all answers to scores
answer_score_dict = {"yes":1,"yesbut":0.75,"nobut":0.25,"no":0}

def _iplot(*args, **kwargs):
  return opy.plot(*args, **kwargs, auto_open=False, output_type='div')

# Function turns answers into scores
def Scoring(answers):
  scores=[]
  for ans in answers:
    scores.append(answer_score_dict[ans])
  return(scores)

# Build Bar charts
def BarGraphs(data):
  data_dict=Counter(data)
  for x in [0,0.25,0.75,1]:
    if x not in  data_dict.keys():
      data_dict[x]=0
  if len(np.unique(data))>1:
    hist=[go.Bar(x=list(data_dict.keys()),y=list(data_dict.values()))]
    layout = go.Layout(xaxis=dict(title="FAIR score (0=no,0.25=nobut,0.75=yesbut,1=yes)",ticks='outside',tickvals=[0,0.25,0.5,0.75,1]),yaxis=dict(title='Responses'),width=400,height=400)
    fig = go.Figure(data=hist, layout=layout)
    yield _iplot(fig)

def RubricPieChart(assessments_with_rubric):
  assessments_with_rubric=assessments_with_rubric.values_list('rubric',flat=True) 
  rubrics_dict=Counter(assessments_with_rubric)
  rubrics=list(rubrics_dict.keys())
  evals=list(rubrics_dict.values())
  evals = [x/9 for x in evals]
  rubric_names=[models.Rubric.objects.current.filter(id=x).values_list('title', flat=True).get() for x in rubrics]
  fig = [go.Pie(labels=rubric_names, values=evals, hoverinfo='label+value+percent', textinfo='percent')]
  yield _iplot(fig)

def RubricsInProjectsOverlay(answers_within_project,projectid):
  rubrics=np.unique(models.Rubric.objects.current.filter(assessments__project__id__in=[projectid]).values_list('id',flat=True))
  all_trace=[]
  for rubric in rubrics:
    responses=answers_within_project.filter(assessment__rubric__id=rubric).values_list('answer',flat=True)
    if len(responses)>0:
      scores_dict=Counter(responses)
      for x in ['no','nobut','yesbut','yes']:
        if x not in scores_dict.keys():
          scores_dict[x]=0
      trace = go.Bar(x=['no (0)', 'no but (0.25)','yes but (0.75)','yes (1)'],y=[scores_dict['no'],scores_dict['nobut'],scores_dict['yesbut'],scores_dict['yes']],
            name= models.Rubric.objects.current.filter(id=rubric).values_list('title', flat=True).get())
      all_trace.append(trace)
  layout = {'xaxis': {'title': 'Answer'},
    'yaxis': {'title': 'Responses'},
    'barmode': 'stack',
  }
  yield _iplot({'data': all_trace, 'layout': layout})

def _QuestionBarGraphs(metric_count_dict):
  hist=[go.Bar(x=list([metric_dict[x] for x in metric_count_dict.keys()]),y=list(metric_count_dict.values()))]
  layout = go.Layout(xaxis=dict(title="Metric",titlefont=dict(size=16),tickfont=dict(size=12)),yaxis=dict(title='Mean FAIR score',titlefont=dict(size=16)))
  fig = go.Figure(data=hist, layout=layout)
  yield _iplot(fig)

def QuestionBreakdown(query):
  metric_ids=iter(np.array(query4.values_list('metric',flat=True)))
  answers=iter(np.array(query4.values_list('answer',flat=True)))
  scores=Scoring(answers)
  d={}
  k = list(zip(metric_ids, scores))
  for (x,y) in k:
    if x in d:
      d[x] = d[x] + y 
    else:
      d[x] = y
  average_score={}
  for key, value in d.items():
    average_score[key]=value/(len(scores)/9)
  return _QuestionBarGraphs(average_score)

def _DigitalObjectBarGraph(scores_dict):
  action_dict={}
  sorted_d = sorted((value,key) for (key,value) in scores_dict.items())
  for kv in sorted_d:
    if kv[0]<0.25:
      action_dict[kv[1]]='Poor'
    if kv[0]>=0.25 and kv[0]<=0.75:
      action_dict[kv[1]]='Good'
    if kv[0]>0.75:
      action_dict[kv[1]]='Very FAIR'
  scores = [sorted_d[x][0] for x in range(0,len(sorted_d))]
  objects=[sorted_d[x][1] for x in range(0,len(sorted_d))]
  all_trace=[]
  for result in [('Poor','rgba(255,10,10,1)'),('Good','rgba(132,0,214,1)'),('Very FAIR','rgba(0,0,214,1)')]:
    X=[]
    Y=[]
    for obj in objects:
      if action_dict[obj]==result[0]:
        X.append(obj)
        Y.append(scores_dict[obj])
    trace=go.Bar(x=X, y=Y,name=result[0],marker=dict(color=result[1]))
    all_trace.append(trace)
  layout=go.Layout(xaxis=dict(title="Resources (n="+str(len(scores))+")",showticklabels=False,titlefont=dict(size=16)),showlegend=True,yaxis=dict(title='Mean FAIR score',titlefont=dict(size=16)))
  fig = go.Figure(data=all_trace, layout=layout)
  yield _iplot(fig)

def DigitalObjectBarBreakdown(project):
  object_score_dict={}
  for obj in project.digital_objects.current.all():
    answers=list(models.Answer.objects.current.filter(assessment__target__id=obj.id).values_list("answer",flat=True))
    if len(answers)>0:
      scores=Scoring(answers)
      mean_score=np.mean(scores)
      object_score_dict[models.DigitalObject.objects.current.filter(id=obj.id).values_list('title', flat=True).get()]=mean_score
  return _DigitalObjectBarGraph(object_score_dict)

# Overall scores for a particular rubric, project, metric...(***Can be placed on each rubric, project, and metric page***)
# Get all scores in the database for a particular rubric, project, or metric 
# Input: Query Set (all answers), type of paramter, parameter ID
# example input query: models.Answer.objects.current.filter(assessment__project__id=11).all() 
def SingleQuery(querySet, PARAM, ID):
  if PARAM=="project":
    title=models.Project.objects.current.filter(id=ID).values_list('title', flat=True).get()
    responses=querySet.values_list('answer', flat=True)
    scores=Scoring(responses)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the project:",models.Project.objects.current.filter(id=ID).values_list('title', flat=True).get(),"(project id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)
  if PARAM=="rubric":
    title=models.Rubric.objects.current.filter(id=ID).values_list('title', flat=True).get()
    responses=querySet.values_list('answer', flat=True)
    scores=Scoring(responses)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the rubric:",models.Rubric.objects.current.filter(id=ID).values_list('title', flat=True).get(),"(rubric id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)
  if PARAM=="metric":
    title=models.Metric.objects.current.filter(id=ID).values_list('title', flat=True).get()
    responses=querySet.values_list('answer', flat=True)
    scores=Scoring(responses)
    if len(scores)!=0:
      print("Overall FAIR Evaluations for the metric:",models.Metric.objects.current.filter(id=ID).values_list('title', flat=True).get(),"(metric id:",ID,")","\n")
      print("Mean FAIR score:",round(np.mean(scores),2))
      print("Median FAIR score:",np.median(scores))
      print("Total Assessments:",len(scores)/9)
      print("Total Questions Answered:",len(scores))
      return BarGraphs(scores)

def TablePlot(project):
  from django.template import Template, Context
  metrics = [
    metric.title
    for obj in project.digital_objects.current.all()
    for assessment in obj.assessments.all()
    for metric in assessment.rubric.metrics.all()
  ]
  objs = [
    obj.title
    for obj in project.digital_objects.current.all()
  ]
  scores = [
    [
      np.mean([
        answer.value()
        for answer in models.Answer.objects.current.filter(metric=metric, assessment__target=obj)
      ])
      for assessment in obj.assessments.all()
      for metric in assessment.rubric.metrics.all()
    ]
    for obj in project.digital_objects.current.all()
  ]
  trace = go.Heatmap(z=scores, x=metrics, y=objs)
  data = [trace]
  layout = go.Layout(xaxis=dict(title="Metrics",ticks='',
        showticklabels=False, automargin=True),yaxis=dict(title='Digital Objects',ticks='',
        showticklabels=True, automargin=True))
  fig = go.Figure(data=data, layout=layout)
  yield _iplot(fig)
