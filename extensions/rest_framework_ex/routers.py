from rest_framework import routers
from FAIRshakeHub.views import index

class APIRootView(routers.APIRootView):
  def get(self, request, *args, **kwargs):
    if request.GET.get('format', 'html') == 'html':
      return index(request)
    else:
      return super().get(request, *args, **kwargs)


class CustomRouter(routers.DefaultRouter):
  root_view_name = 'index'
  APIRootView = APIRootView
