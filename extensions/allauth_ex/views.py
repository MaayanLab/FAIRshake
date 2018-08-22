from allauth.account.views import LogoutView
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.orcid.views import OrcidOAuth2Adapter
from allauth.socialaccount.providers.globus.views import GlobusAdapter

class GithubLogin(SocialLoginView):
  adapter_class = GitHubOAuth2Adapter

class OrcidLogin(SocialLoginView):
  adapter_class = OrcidOAuth2Adapter

class GlobusLogin(SocialLoginView):
  adapter_class = GlobusAdapter

class DeleteAccountView(LogoutView):
  template_name = "account/delete.html"
  redirect_field_name = "next"

  def logout(self):
    user = self.request.user
    if user.is_authenticated:
      user.delete()
    return super().logout()

account_delete = DeleteAccountView.as_view()
