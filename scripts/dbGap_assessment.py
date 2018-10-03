import re
import sys
import json
import xml.etree.ElementTree as ET
from ftplib import FTP
from io import BytesIO

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAIRshake.settings")
import django
django.setup()
from FAIRshakeAPI import models

metrics = [
  {
    'query': './/Studies/Study[@accession]',
    'desc': 'ID or accession number',
    'metric': 21,
    'pattern': None,
  },
#   {
#     'query': './/Studies/Study',
#     'desc': 'Has metadata',
#     'metric': 22,
#     'pattern': None,
#   },
  {
#     'query': './/MetaVariables/Submitter/Method',
    'query': './/Analyses/Analysis/Method',
    'desc': 'Experimental method',
    'metric': 23,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Studies/Study[@source]',
    'desc': 'established data repository',
    'metric': 24,
    'pattern': None,
  },
  {
    'query': './/Documents/Document',
    'desc': 'Downloadable',
    'metric': 25,
    'pattern': None,
  },
  {
    'query': './/Studies/Study[@accession]',
    'desc': 'Has version information', # versioning info is within accession number 
    'metric': 26,
    'pattern': None,
  },
  {
    'query': './/DacInfo/DacEmail',
    'desc': 'Has contact',
    'metric': 27,
    'pattern': re.compile(r'.+@.+'),
  },
  {
    'query': './/Publications/Publication',
    'desc': 'Citable',
    'metric': 28,
    'pattern': None,
  },
  {
    'query': './/AuthorizedAccess/Policy',
    'desc': 'Usage Protocol/License',
    'metric': 29,
    'pattern': None,
  },
  {
    'query': './/StudyNameEntrez',
    'desc': 'Has a title',
    'metric': 60,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Description',
    'desc': 'Has a description',
    'metric': 63,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Documents/Document[@uID]',
    'desc': 'Unique identifier in dbGaP Entrez system',
    'metric': 87,
    'pattern': None,
  },
  {
    'query': './/Studies/Study',
    'desc': 'Machine readable metadata',
    'metric': 89,
    'pattern': None,
  },
   {
    'query': './/DocumentSet/DataUseCertificate[@FilePath]',
    'desc': 'URL to data usage limitations',
    'metric': 92,
    'pattern': None,
  },
    {
    'query': './/DocumentSet/DataUseCertificate[@FilePath]',
    'desc': 'URL to protocol to access restricted content',
    'metric': 111,
    'pattern': None,
  },
  {
    'query': './/Studies/Study[@modDate]',
    'desc': 'Date last updated/modified',
    'metric': 120,
    'pattern': None,
  },
  {
    'query': './/Attributions/Header',
    'desc': 'Has attribution',
    'metric': 121,
    'pattern': None,
  },
#   {
#     'query': './/Analyses/Analysis',
#     'desc': 'Summary Statistics',
#     'pattern': None,
#   },
]

studies = [
  'phs000007',
  'phs000179',
  'phs000200',
  'phs000209',
  'phs000280',
  'phs000284',
  'phs000285',
  'phs000286',
  'phs000287',
  # 'phs000424', # TODO: put in Gtex
  'phs000920',
  'phs000921',
  'phs000946',
  'phs000951',
  'phs000954',
  'phs000956',
  'phs000964',
  'phs000974',
  'phs000988',
  'phs000993',
  'phs000997',
  'phs001013',
  'phs001024',
  'phs001032',
  'phs001040',
  'phs001062',
  'phs001143',
  'phs001189',
  'phs001211',
]

res = {}
with FTP('ftp.ncbi.nlm.nih.gov') as ftp:
  ftp.login()
  for study in studies:
    # Go to study directory
    ftp.cwd('/dbgap/studies/%s/' % (study))
    # Enumerate directories
    dirs = ftp.nlst()
    # Use the last (latest)
    ftp.cwd([d for d in dirs if d.startswith(study)][-1])
    # Enumerate files
    files = ftp.nlst()
    try:
      # Find the xml file
      meta = [file for file in files if file.endswith('.xml')][0]
      # Download it
      meta_file = BytesIO()
      ftp.retrbinary('RETR ' + meta, meta_file.write)
      # Get it
      xml = meta_file.getvalue().decode()
      # Parse it
      root = ET.fromstring(xml)
      # Look for metrics
      answers = {
        'meta': meta
      }
      for metric in metrics:
        matches = root.findall(metric['query'])
        if metric['pattern']:
          results = ' '.join([e.text.strip() for e in matches]).strip()
        else:
          results = metric['query']
        answers[metric['desc']] = {
          'metric': metric.get('metric',''),
          'answer': 'yes' if matches and (metric['pattern'] is None or metric['pattern'].match(results)) else 'no',
          'comment': results,
        }
    except Exception as e:
      print(study+':', e, file=sys.stderr)
      answers = {
        'meta': None,
      }
      
    # Find the data dict and variabe report in pheno_variable_summaries folder
    try:
      ftp.cwd('pheno_variable_summaries')
      files = ftp.nlst()

      datadict = [file for file in files if file.startswith('datadict')][0]
      varreport = [file for file in files if file.startswith('varreports')][0]
      answers['Standardized metadata'] = {
        'metric': 107,
        'answer': 'yes',
        'comment': 'data dictionary and variable report exists'
      }
    except Exception as e:
      print(study+':'+' Variable report and data dictionary not found')
      answers['Standardized metadata'] = {
        'metric': 107,
        'answer': 'no',
        'comment': 'data dictionary and variable report not found'
      }
    # variable terms between studies are currently not interoperable or community-accepted
    #   and no way to assert this
    answers['Variables linked to standards'] = {
      'metric': 95,
      'answer': 'no',
      'comment': 'Variables are not represented using a formal, accessible, and broadly applicable language'
    }
    res[study] = answers

me = models.Author.objects.get(username='maayanlab')
topmed = models.Project.objects.get(id=61)
dbgap_rubric = models.Rubric.objects.get(id=26)
objs = []
assessments = []
for study, answers in res.items():
  if not answers['meta']:
    continue
  obj = models.DigitalObject.objects.get(
    url='ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/%s/' % (study)
  )
  obj.rubrics.add(dbgap_rubric)
  objs.append(obj)
  assessment = models.Assessment(
    project=topmed,
    target=obj,
    rubric=dbgap_rubric,
    methodology='auto',
    assessor=me,
  )
  assessment.save()
  assessments.append(assessment)
  for metric, ans in answers.items():
    if metric == 'meta' or ans['metric'] is None:
      continue
    answer = models.Answer(
      assessment=assessment,
      metric=models.Metric.objects.get(id=ans['metric']),
      answer=ans['answer'],
      comment=ans['comment'],
    )
    answer.save()

# for assessment in assessments:
#   assessment.delete()
# assessments[0].delete()
# for obj in objs:
#   obj.delete()
# objs[0].delete()