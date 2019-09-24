import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAIRshake.settings")
import django
django.setup()

from FAIRshakeAPI import models

def merge_attr(obj, attr, *dups):
  P = set([getattr(dup, attr) for dup in [obj]+list(dups)])
  if len(P) > 1:
    selections = {str(i): p for i, p in enumerate(P)}
    for i, p in enumerate(P):
      print('(%d%s) %s' % (i, '*' if p == getattr(obj, attr) else '', p))
    inp = input()
    if inp == '':
      selection = getattr(obj, attr)
    elif selections.get(inp) is not None:
      selection = selections[inp]
    else:
      selection = inp
  else:
    selection = getattr(obj, attr)
  setattr(obj, attr, selection)

def merge_many_attr(obj, attr, *dups):
  for dup in dups:
    for child in getattr(dup, attr).all():
      getattr(obj, attr).add(child)

def merge_dups(primary, *dups):
  for attr in ['title', 'url', 'description', 'image', 'tags', 'type', 'fairmetrics']:
    merge_attr(primary, attr, *dups)
  for attr in ['authors', 'rubrics', 'projects', 'assessments']:
    merge_many_attr(primary, attr, *dups)
  for dup in dups:
    dup.delete()

# Find and merge full duplicates digital objects (objects that serialize out to be the same)
import json
from django.core import serializers
def custom_json(*objs):
  JSON = json.loads(serializers.serialize('json', objs))
  for obj in JSON:
    del obj['pk']
  return json.dumps(JSON)
potential_full_dups = {}
for obj in models.DigitalObject.objects.all():
  j = custom_json(obj)
  potential_full_dups[j] = potential_full_dups.get(j, []) + [obj]
full_dups = {
  j: dups
  for j, dups in potential_full_dups.items()
  if len(dups) > 1
}
full_dups

for _, dups in full_dups.items():
  obj = dups[0]
  merge_dups(dups[0], *dups[1:])

# Find and potentially merge url duplicate digital objects (objects with identical urls)
potential_url_dups = {}
for obj in models.DigitalObject.objects.all():
  if obj.url != '':
    potential_url_dups[obj.url] = potential_url_dups.get(obj.url, []) + [obj]
url_dups = {
  url: dups
  for url, dups in potential_url_dups.items()
  if len(dups) > 1
}
for url, dups in url_dups.items():
  print(
    'Merge',
    *dups,
    'Y/n',
    sep='\n',
  )
  resp = input()
  if resp.lower() == 'y' or resp == '':
    merge_dups(dups[0], *dups[1:])
  elif resp.lower() == 'n':
    continue
  else:
    for rs in [r.split(',') for r in resp.split(' ')]:
      merge_dups(rs[0], *rs[1:])
