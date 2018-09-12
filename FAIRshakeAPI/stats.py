from . import models
import plotly.offline as opy
import plotly.graph_objs as go
from collections import Counter
import numpy as np

def _iplot(*args, **kwargs):
  return opy.plot(*args, **kwargs, auto_open=False, output_type='div')

# Function turns answers into scores
def Scoring(answers):
  return [answer.inverse() for answer in answers]

def RubricsInProjectsOverlay(project):
    query = models.Answer.objects.filter(assessment__project__id = project.id).all()
    rubrics = np.unique(models.Rubric.objects.filter(assessments__project__id__in=[project.id]).values_list('id',flat=True))
    all_trace = []
    for rubric in rubrics:
        responses = query.filter(assessment__rubric__id = rubric).values_list('answer',flat=True)
        if len(responses) > 0:
            responses_dict=Counter(responses)
            for x in list(responses_dict.keys()):
                 if x not in list(answer_dict.keys()):
                    responses_dict[x] = 0
            x = [reverse_answer_dict[x] for x in sorted(answer_dict.values())]
            y = [responses_dict[y] for y in x]
            trace = go.Bar(x=x,y=y,name=models.Rubric.objects.filter(id=rubric).values_list('title', flat=True).get())
            all_trace.append(trace)
    layout = {'xaxis': {'title': 'Answer'},'yaxis': {'title': 'Responses'},'barmode': 'stack'}
    yield _iplot({'data': all_trace, 'layout': layout})

def RubricPieChart(project):
    objects = list(project.values_list('digital_objects', flat=True))
    rubrics = np.unique(project.assessments.values_list('rubric',flat=True))
    rubric_object_dict = {}
    for rubric in rubrics:
        rubric_object_dict[rubric] = 0 
    for obj in objects:
        associated_rubrics = list(models.DigitalObject.objects.filter(id = obj).values_list('rubrics', flat=True))
        for x in associated_rubrics:
            rubric_object_dict[x] += 1
    rubric_names = [models.Rubric.objects.filter(id=x).values_list('title', flat=True).get() for x in list(rubric_object_dict.keys())]
    object_counts = list(rubric_object_dict.values())
    fig = [go.Pie(labels=labels, values=values, hoverinfo='label+value+percent', textinfo='percent')]
    yield iplot(fig)

def DigitalObjectScoreHist(project):
    objects = project.values_list('digital_objects',flat=True)
    object_score_dict = {}
    for obj in objects:
        answers = list(models.Answer.objects.filter(assessment__target__id=obj,assessment__project__id = project.id).values_list("answer",flat=True))
        if len(answers) > 0:
            scores = Scoring(answers)
            mean_score = np.mean(scores)
            object_score_dict[models.DigitalObject.objects.filter(id=obj).values_list('title', flat=True).get()]=mean_score
    labels_dict={}
    sorted_object_score_dict = sorted((value,key) for (key,value) in object_score_dict.items())
    for kv in  sorted_object_score_dict:
        if kv[0]<0.25:
            labels_dict[kv[1]] = 'Poor'
        if kv[0]>=0.25 and kv[0]<=0.75:
            labels_dict[kv[1]] = 'Good'
        if kv[0]>0.75:
            labels_dict[kv[1]] = 'Very FAIR'
    scores_sorted = [sorted_object_score_dict[x][0] for x in range(0,len(sorted_object_score_dict))]
    objects_sorted = [sorted_object_score_dict[x][1] for x in range(0,len(sorted_object_score_dict))]
    all_trace=[]
    for result in [(k,v) for k,v in color_dict.items()]:
        X=[]
        Y=[]
        for obj in objects_sorted:
            if labels_dict[obj]==result[0]:
                X.append(obj)
                Y.append(object_score_dict[obj])
        trace=go.Bar(x=X, y=Y,name=result[0],marker=dict(color=result[1]))
        all_trace.append(trace)
    layout=go.Layout(xaxis=dict(title="Resources (n="+str(len(scores_sorted))+")",showticklabels=False,titlefont=dict(size=16)),showlegend=True,yaxis=dict(title='Mean FAIR score',titlefont=dict(size=16)))
    fig = go.Figure(data=all_trace, layout=layout)
    yield iplot(fig)

def ColorMap(project):
    objects = project.values_list('digital_objects',flat=True)
    unique_metrics=np.unique(models.Answer.objects.filter(assessment__project__id=project.id).values_list('metric',flat=True))
    metric_matrix=[]
    for obj in objects:
        responses= list(models.Answer.objects.filter(assessment__target__id=obj,assessment__project__id = project.id).values_list("answer",flat=True))
        responses=Scoring(responses)
        metrics = list(models.Answer.objects.filter(assessment__target__id=obj,assessment__project__id = project.id).values_list("metric",flat=True))
        metrics_avg_score={}
        for i,m in enumerate(metrics):
            if m not in metrics_avg_score.keys():
                metrics_avg_score[m]=[]
                metrics_avg_score[m].append(responses[i])
            else:
                metrics_avg_score[m].append(responses[i])
        for k,v in metrics_avg_score.items():
            metrics_avg_score[k]=np.mean(v)
        
        all_metric_ans=[]
        for m in unique_metrics:
            try:
                all_metric_ans.append(metrics_avg_score[m])
            except:
                all_metric_ans.append(-1)
        metric_matrix.append(all_metric_ans)
    cmap = colors.ListedColormap(['grey','red', 'darkviolet','indigo','blue'])
    bounds = [-1,0,0.25,0.75,0.9,1]
    norm = colors.BoundaryNorm(bounds, cmap.N)
    fig, ax = plt.subplots(figsize=(100, 100))
    ax.matshow(metric_matrix, cmap=cmap, norm=norm)

    ax.xaxis.set_ticks(np.arange(0.5, int(len(unique_metrics))+0.5, 1) - 0.5, minor=True)
    ax.xaxis.set(ticks=np.arange(0, int(len(unique_metrics)), 1), ticklabels=unique_metrics)
    ax.yaxis.set_ticks(np.arange(0.5, int(len(objects)), 1) - 0.5, minor=True)
    ax.yaxis.set(ticks=np.arange(0, int(len(objects)), 1),ticklabels=objects)
    ax.tick_params(axis='both', labelsize=15,rotation=45,width=4,length=7)
    minor_locator = FixedLocator(np.arange(0.5, len(unique_metrics), 0.5))
    ax.xaxis.set_minor_locator(minor_locator)
    plt.grid(which='minor',axis='both', linestyle='-', color='k',linewidth=1)
    legend_elements = [Patch(facecolor='grey', edgecolor='grey',
                             label='Not assessed'),
                        Patch(facecolor='blue', edgecolor='blue',
                             label='Yes'),
                           Patch(facecolor='indigo', edgecolor='indigo',
                             label='Yes but'),
                        Patch(facecolor='darkviolet', edgecolor='darkviolet',
                             label='No but'),
                           Patch(facecolor='red', edgecolor='r',
                             label='No')]
    plt.legend(handles=legend_elements, title="Answer",bbox_to_anchor=(1.05, 1), loc=2,prop={'size': 15})
    plt.show()

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
