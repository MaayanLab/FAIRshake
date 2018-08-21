from drf_yasg.generators import OpenAPISchemaGenerator
from django.conf import settings

class CustomSchemaGenerator(OpenAPISchemaGenerator):
  def get_schema(self, *args, **kwargs):
    swagger = super(CustomSchemaGenerator, self).get_schema(*args, **kwargs)
    # TODO: This should probably be a bit more generic / based on settings
    swagger.tags = [
      { 'name': 'NIHdatacommons' },
      { 'name': 'Maayanlab' },
    ]
    swagger['info']['contact']['x-role'] = 'responsible organization'
    return swagger
