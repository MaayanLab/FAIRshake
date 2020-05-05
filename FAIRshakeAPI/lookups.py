from django.db.models import Lookup
from django.db.models.fields import TextField

def _sql_concat(lhs, rhs):
  return '{lhs} || {rhs}'.format(lhs=lhs, rhs=rhs)

def _mysql_concat(lhs, rhs):
  return 'CONCAT({lhs}, {rhs})'.format(lhs=lhs, rhs=rhs)

def _sql_is_instr(lhs, rhs):
  return '''INSTR({lhs}, {rhs}) > 0'''.format(lhs=lhs, rhs=rhs)

def _sql_replace(lhs, substr, repl):
  return '''REPLACE({lhs}, {substr}, {repl})'''.format(lhs=lhs, substr=substr, repl=repl)

def _sql_case(*kargs):
  args, last_arg = kargs[:-1], kargs[-1]
  return '''
    CASE
      {}
      ELSE {}
    END
  '''.format(
    '\n'.join('WHEN {} THEN {}'.format(arg['when'], arg['then']) for arg in args),
    last_arg,
  )

@TextField.register_lookup
class UrlSimilar(Lookup):
  lookup_name = 'url_similar'

  def as_sql(self, compiler, connection, _concat=_sql_concat, **kwargs):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = (lhs_params*1) + (rhs_params*3)
    return _sql_is_instr(
      _sql_replace(
        _sql_replace(
          lhs,
          "'http://'",
          "'https://'"
        ),
        "'https://www.'",
        "'https://'"
      ),
      _sql_replace(
        _sql_replace(
          _sql_case(
            dict(when=_sql_is_instr(rhs, "'://'"), then=rhs),
            _concat("'https://identifiers.org/'", rhs)
          ),
          "'http://'",
          "'https://'"
        ),
        "'https://www.'",
        "'https://'"
      ),
    ), params

  def as_mysql(self, *args, _concat=_mysql_concat, **kwargs):
    return self.as_sql(*args, _concat=_concat, **kwargs)

@TextField.register_lookup
class UrlStrict(Lookup):
  lookup_name = 'url_strict'

  def as_sql(self, compiler, connection, _concat=_sql_concat, **kwargs):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = (lhs_params*1) + (rhs_params*3)
    return _sql_is_instr(
      _sql_replace(
        _concat(
          _sql_replace(
            _sql_replace(
              lhs,
              "'http://'",
              "'https://'"
            ),
            "'https://www.'",
            "'https://'"
          ),
          "'\n'",
        ),
        "'\r\n'",
        "'\n'"
      ),
      _sql_replace(
        _concat(
          _sql_replace(
            _sql_replace(
              _sql_case(
                dict(when=_sql_is_instr(rhs, "'://'"), then=rhs),
                _concat("'https://identifiers.org/'", rhs)
              ),
              "'http://'",
              "'https://'"
            ),
            "'https://www.'",
            "'https://'"
          ),
          "'\n'"
        ),
        "'\r\n'",
        "'\n'"
      )
    ), params

  def as_mysql(self, *args, _concat=_mysql_concat, **kwargs):
    return self.as_sql(*args, _concat=_concat, **kwargs)
