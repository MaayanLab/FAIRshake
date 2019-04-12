from django.http import QueryDict

def query_dict(*args, **kwargs):
  if len(args) > 0 and isinstance(args[0], QueryDict):
    qd = args[0].copy()
    args = args[1:]
  else:
    qd = QueryDict(mutable=True)
  for arg in list(args)+[kwargs]:
    assert isinstance(arg, dict) or isinstance(arg, QueryDict), type(arg)
    for k, v in arg.items():
      qd[k] = v
  return qd
