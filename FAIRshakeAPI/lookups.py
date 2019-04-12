from django.db.models import Lookup
from django.db.models.fields import TextField

@TextField.register_lookup
class UrlSimilar(Lookup):
  lookup_name = 'url_similar'

  def as_sql(self, compiler, connection):
    lhs, lhs_params = self.process_lhs(compiler, connection)
    rhs, rhs_params = self.process_rhs(compiler, connection)
    params = lhs_params + rhs_params
    return '''
    INSTR(
      REPLACE(REPLACE({0}, 'http://', 'https://'), 'https://www.', 'https://'),
      REPLACE(REPLACE({1}, 'http://', 'https://'), 'https://www.', 'https://')
    ) > 0
    '''.format(lhs, rhs), params
