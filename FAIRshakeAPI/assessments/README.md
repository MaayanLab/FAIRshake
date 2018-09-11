# Assessments

Assessment modules can be added to this directory and will be automatically incorporated in FAIRshake. Each module should expose a single function of the form:

```python
class Assessment:
  inputs: [
    'target:url', # Require the target url attribute
    'answer:1', # Require the answer to metric 1
  ]
  outputs: [
    'answer:2', # Results in the answer to metric 2
  ]

  def perform(inputs):
    # Perform the assessment returning answers you support
    return {
      output_id: output,
    }
```
