''' Usage:
from pyswagger_wrapper import SwaggerClient

client = SwaggerClient('your_swagger_url', headers={'auth': 'whatever', 'if': 'necessary'})
client.actions.your_op_id.call(your=params)
'''

import json
from urllib import request
from pyswagger import App
from pyswagger.getter import SimpleGetter
from pyswagger.contrib.client.requests import Client

class SwaggerClient:
  def __init__(self, url, headers={}):
    self._headers = headers
    self._url = url
    self._update()

  def update(self, url=None, headers=None):
    if url is not None:
      self._url = url
    if headers is not None:
      self._headers = headers
    self._update()

  def request(self, path, *args, **kwargs):
    return json.loads(
      self._client.request(
        self._app.op[path if type(path) == str else '!##!'.join(path)](
          *args,
          **kwargs,
        ),
        headers=self._headers,
      ).raw.decode()
    )

  def _update(self):
    self._app = self._create_app(self._url, headers=self._headers)
    self._client = self._create_client()
    self._update_magic()

  def _update_magic(self):
    self.models = type('Models', (object,), dict(self._create_models()))
    self.actions = type('Actions', (object,), dict(self._create_actions()))
  
  def _create_models(self):
    for model_name, model in self._app.m.items():
        yield (model_name, type(model_name, (object,), model.properties))

  def _create_actions(self):
    for k, v in self._app.op.items():
      name = k.split('!##!')[-1]
      v.call = lambda *args, __self=self, __k=k, **kwargs: __self.request(__k, *args, **kwargs)
      v.call.__doc__ = v.description
      yield (name, v)

  def _create_app(self, url, headers={}):
    app = App.load(url, getter=self._create_getter(headers=headers))
    app.prepare(strict=False)
    return app

  def _create_getter(self, headers={}):
    def getter(url):
      return request.urlopen(
        request.Request(
          url,
          headers=headers,
        )
      ).read()

    class Getter(SimpleGetter):
      __simple_getter_callback__ = getter

    return Getter

  def _create_client(self):
    return Client()