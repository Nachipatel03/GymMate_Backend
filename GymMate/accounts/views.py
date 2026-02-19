from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from members.serializers import MemberRegisterSerializer


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MemberRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MemberRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        member = serializer.save()

        return Response(
            {
                "message": "Registration successful. Please wait for verification.",
                "member_id": member.id,
                "email": member.user.email,
                "is_verified": member.user.is_verified,
            },
            status=status.HTTP_201_CREATED
        )