import json
import pprint
from jsondiff import diff

def prompt_merge_attr(*attrs_list):
  ''' Given multiple versions of an attribute dictionary,
  facilitate merging them into a single version.
  '''
  final_attrs = {}
  all_attrs = set([
    attr
    for attrs in attrs_list
    for attr in attrs.keys()
  ])
  for attr in all_attrs:
    # Create numbered list of unique non-null options
    attr_vals = {
      str(n + 1): attr_val
      for n, attr_val in enumerate(
        filter(lambda s: json.loads(s), set([
          json.dumps(attrs.get(attr))
          for attrs in attrs_list
        ]))
      )
    }
    # If only one option, use it
    if len(attr_vals) == 1:
      _, attr_val = attr_vals.popitem()
      final_attrs[attr] = json.loads(attr_val)
      continue
    elif len(attr_vals) == 0:
      final_attrs[attr] = ''
      continue
    # Prompt user to select option or provide their own value
    print('Select or provide value for "%s":' % (attr))
    for n, attr_val in attr_vals.items():
      print('(%s) %s' % (n, attr_val))
    print('> ', end='')
    # Use value selected or fall back to their custom value
    inp = input()
    attr_val = attr_vals.get(inp, inp)
    try:
      final_attrs[attr] = json.loads(attr_val)
    except:
      final_attrs[attr] = attr_val
  return final_attrs

def prompt_select_dups(*attrs_list):
  # Just select the 1 if there is only 1
  if len(attrs_list) == 1:
    yield attrs_list[0]
    return
  # Create numbered list of potential dups
  attr_vals = {
    str(n + 1): attr_list
    for n, attr_list in enumerate(attrs_list)
  }
  # Prompt user to select dups
  print('Select dups (e.g. 1,2 3,4,5,6):')
  print(pprint.pformat(attr_vals['1']))
  for n, attr_val in attr_vals.items():
    print('(%s) %s' % (n, pprint.pformat(diff(attr_vals['1'], attr_val))))
  print('> ', end='')
  inp = input()
  if inp != '':
    for dups in inp.split(' '):
      yield prompt_merge_attr(*[
        attr_vals[dup]
        for dup in dups.split(',')
      ])
