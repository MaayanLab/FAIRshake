class Assessment:
  inputs = [
    'target',
  ]
  outputs = [
    'metric:1', # Unique name and informative description
    'metric:2', # Accessed from a webpage
  ]
  def perform(inputs):
    target = inputs['target']
    return {
      'metric:1': 'yes' if target.title and target.description else 'no',
      'metric:2': 'yes' if target.url else 'no',
    }
