from allauth.account.views import LogoutView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.globus.views import GlobusAdapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateResponseMixin, View
from rest_auth.registration.views import SocialLoginView
from rest_framework.authtoken.models import Token

class GithubLogin(SocialLoginView):
  adapter_class = GitHubOAuth2Adapter

class OrcidLogin(SocialLoginView):
  adapter_class = OrcidOAuth2Adapter

class GlobusLogin(SocialLoginView):
  adapter_class = GlobusAdapter

class APIAccessAccountView(TemplateResponseMixin, View):
  template_name = "account/api_access.html"

  def get(self, *args, **kwargs):
    ctx = self.get_context_data()
    return self.render_to_response(ctx)

  def get_context_data(self, **kwargs):
    context = kwargs
    context['api_key'] = Token.objects.get_or_create(
      user=self.request.user
    )[0]
    return context

account_api_access = login_required(APIAccessAccountView.as_view())

class DeleteAccountView(LogoutView):
  template_name = "account/delete.html"
  redirect_field_name = "next"

  def logout(self):
    user = self.request.user
    if user.is_authenticated:
      user.delete()
    return super().logout()

account_delete = login_required(DeleteAccountView.as_view())
