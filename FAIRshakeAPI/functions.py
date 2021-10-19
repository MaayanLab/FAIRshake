from django.db.models import F, Aggregate

Q1 = lambda col: Aggregate(
  F(col),
  function="percentile_cont",
  template="%(function)s(0.25) WITHIN GROUP (ORDER BY %(expressions)s)",
)
Median = lambda col: Aggregate(
  F(col),
  function="percentile_cont",
  template="%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)",
)
Q3 = lambda col: Aggregate(
  F(col),
  function="percentile_cont",
  template="%(function)s(0.75) WITHIN GROUP (ORDER BY %(expressions)s)",
)
