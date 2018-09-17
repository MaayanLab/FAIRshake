import logging

assessments = []

class Assessment:
  def perform(target, rubric):
    want = ['metric:%d' % (metric.id) for metric in rubric.metrics.all()]
    have = dict({
        'target:%s' % (attr): v
        for attr, v in target.attrs().items()
        if v
      },
      target=target,
      rubric=rubric,
    )
    performed = set()
    cant_get = []

    # The below loop uses assessments to turn want into have as much as possible
    #  potentially adding more wants if an assessment has something in particular
    #  but has a dependency
    while want != []:
      # Try to obtain our current want
      current_want = want.pop()
      if have.get(current_want) is not None:
        # We already have this, skip
        continue
      current_assessments = set(assessments).difference(performed)
      if not current_assessments:
        break
      for assessment in current_assessments:
        # Does this assessment have what we want
        if current_want in assessment.outputs:
          # Do we have additional needs for this assessment
          current_wants = [
            k
            for k in assessment.inputs
            if k not in have.keys()
          ]
          # Additional needs
          if current_wants:
            # We already tried this and failed, so we are dropping this want
            if current_want in cant_get:
              continue
            # Figure out additional wants
            additional_wants = [
              k
              for k in current_wants
              if k not in want
            ]
            # Put additional wants in the front and this want on the back
            want = additional_wants + want + [current_want]
            # Put the current_want in can't get, if we reach it again but still can't get it
            #  we have to drop it.
            cant_get += want
          else:
            # Get everything ready
            current_have = {
              k: have[k]
              for k in assessment.inputs
            }
            # Perform assessment
            results = assessment.perform(current_have)
            performed.add(assessment)

            # Warn if assessment isn't actually working properly
            if set(list(results.keys())) != set(assessment.outputs):
              logging.warn(
                assessment.__name__ + "'s output is malformed"
              )

            for output_key, output in results.items():
              # We now have these results
              # TODO: smarter collision detection
              if have.get(output_key) is None and output:
                have[output_key] = output

    return have
