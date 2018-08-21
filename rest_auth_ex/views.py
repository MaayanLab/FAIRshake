from rest_framework import generics, permissions
from rest_auth.serializers import UserDetailsSerializer

class UserDetailsViewEx(generics.RetrieveUpdateDestroyAPIView):
  serializer_class = UserDetailsSerializer
  permission_classes = (permissions.IsAuthenticated,)

  def get_object(self):
      return self.request.user
