from django.db.models import Lookup
from django.db.models.fields import TextField

def _sql_concat(lhs, rhs):
  return '{lhs} || {rhs}'.format(lhs=lhs, rhs=rhs)

def _mysql_concat(lhs, rhs):
  return 'CONCAT({lhs}, {rhs})'.format(lhs=lhs, rhs=rhs)

@TextField.register_lookup
class UrlSimilar(Lookup):
  lookup_name = 'url_similar'

  def as_sql(self, compiler, connection, _concat=_sql_concat, **kwargs):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = (lhs_params*3) + (rhs_params*3)
    return '''
    INSTR(
      REPLACE(
        REPLACE(
          CASE
            WHEN INSTR({lhs}, '://') > 0 THEN {lhs}
            ELSE {lhs_full}
          END,
          'http://',
          'https://'
        ),
        'https://www.',
        'https://'
      ),
      REPLACE(
        REPLACE(
          CASE
            WHEN INSTR({rhs}, '://') > 0 THEN {rhs}
            ELSE {rhs_full}
          END,
          'http://',
          'https://'
        ),
        'https://www.',
        'https://
      ')
    ) > 0
    '''.format(
      lhs=lhs,
      lhs_full=_concat("'https://identifiers.org/'", lhs),
      rhs=rhs,
      rhs_full=_concat("'https://identifiers.org/'", rhs),
    ), params

  def as_mysql(self, *args, _concat=_mysql_concat, **kwargs):
    return self.as_sql(*args, _concat=_concat, **kwargs)
