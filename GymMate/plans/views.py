from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import MembershipPlan
from .serializers import MembershipPlanSerializer
from rest_framework import permissions
# Create your views here.
class MembershipPlanCreateAPIView(APIView):
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        
        plans = MembershipPlan.objects.filter(is_active=True)
        serializer = MembershipPlanSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        if not user.is_active:
            return Response(
                {"detail": "Inactive users cannot create membership plans"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MembershipPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )