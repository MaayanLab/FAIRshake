import re
import sys
import json
import xml.etree.ElementTree as ET
from ftplib import FTP
from io import BytesIO

metrics = [
  {
    'query': './/StudyNameEntrez',
    'desc': 'Has a title',
    'metric': 60,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Studies/Study',
    'desc': 'Has metadata',
    'metric': 22,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Description',
    'desc': 'Has a description',
    'metric': 63,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Publications/Publication',
    'desc': 'Citable',
    'metric': 28,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Studies/Study[@source]',
    'desc': 'established data repository',
    'metric': 24,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Attributions/Header',
    'desc': 'Has attribution',
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/DacInfo/DacEmail',
    'desc': 'Has contact',
    'metric': 27,
    'pattern': re.compile(r'.+@.+'),
  },
  {
    'query': './/AuthorizedAccess/Policy',
    'desc': 'Usage Protocol/License',
    'metric': 29,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Documents/Document',
    'desc': 'Downloadable',
    'metric': 25,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Analyses/Analysis',
    'desc': 'Summary Statistics',
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/Studies/Study[@accession]',
    'desc': 'Has version information', # versioning info is within accession number 
    'metric': 26,
    'pattern': re.compile(r'.*'),
  },
  {
    'query': './/MetaVariables/Submitter/Method',
    'desc': 'Experimental method',
    'metric': 23,
    'pattern': re.compile(r'.+'),
  },
  {
    'query': './/Studies/Study[@accession]',
    'desc': 'ID or accession number',
    'metric': 21,
    'pattern': re.compile(r'.*'),
  },
]

studies = [
  'phs000920',
  'phs000921',
  'phs001024',
  'phs000951',
  'phs000946',
  'phs000179',
  'phs000209',
  'phs000424',
  'phs001143',
  'phs001062',
  'phs001032',
  'phs000997',
  'phs000993',
  'phs001189',
  'phs001211',
  'phs001040',
  'phs000956',
  'phs000974',
  'phs000988',
  'phs000964',
  'phs000954',
  'phs001013',
  'phs000007',
  'phs000286',
  'phs000284',
  'phs000200',
  'phs000280',
  'phs000287',
  'phs000285',
]

with sys.stdout as outfile:
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
          results = ' '.join([e.text.strip() for e in matches]).strip()
          answers[metric['desc']] = {
            'metric': metric.get('metric',''),
            'answer': 'yes' if matches and metric['pattern'].match(results) else 'no',
            'comment': results,
          }
      except Exception as e:
        print(study+':', e, file=sys.stderr)
        answers = {
          'meta': None,
        }
      json.dump({
        study: answers,
      }, outfile)
