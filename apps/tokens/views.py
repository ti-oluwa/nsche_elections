from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import response, status, exceptions

from .models import AuthToken


class AuthTokenAuthenticationAPIView(ObtainAuthToken):
    """API view for authenticating users and generating tokens"""

    def get_response_data(self, token: AuthToken) -> dict:
        """
        Returns the response data for a successful authentication.
        Override this method to return custom data.
        By default, it returns the token key and user pk.

        :param token: The authentication token
        :return: The response data
        """
        return {
            "token": token.key,
            "user_id": token.user.pk,
        }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except exceptions.ValidationError:
            return response.Response(
                data={"message": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.validated_data["user"]
        token, _ = AuthToken.objects.get_or_create(user=user)
        data = self.get_response_data(token)
        return response.Response(data=data, status=status.HTTP_200_OK)
