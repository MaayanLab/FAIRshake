from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings
from FAIRshakeAPI import search

from allauth.account.views import LogoutView
class DeleteAccountView(LogoutView):
  template_name = "account/delete.html"
  redirect_field_name = "next"

  def logout(self):
    user = self.request.user
    if user.is_authenticated:
      user.delete()
    return super().logout()

account_delete = DeleteAccountView.as_view()

def index(request):
  ''' FAIRshakeHub Home Page
  '''
  q = request.GET.get('q', '')
  page = request.GET.get('page', 1)
  page_size = settings.REST_FRAMEWORK['SEARCH_PAGE_SIZE']
  items = [
    result
    for vector in [
      search.ProjectSearchVector(),
      search.DigitalObjectSearchVector(),
      search.RubricSearchVector(),
      search.MetricSearchVector(),
    ]
    for result in (vector.query(q) if q else [])
  ]
  paginator = Paginator(
    items,
    page_size,
  )

  return render(request, 'fairshake/index.html', dict(
      query=q,
      items=paginator.get_page(page),
    )
  )

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html')

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html')

def api_documentation(request):
  return render(request, 'fairshake/api_documentation.html')

def terms_of_service(request):
  return render(request, 'fairshake/terms_of_service.html')

def privacy_policy(request):
  return render(request, 'fairshake/privacy_policy.html')
