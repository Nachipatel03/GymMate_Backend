from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import MembershipPlan
from .serializers import MembershipPlanSerializer
from rest_framework import permissions
from django.shortcuts import get_object_or_404


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
class MembershipPlanDetailAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get_object(self, pk):
        return get_object_or_404(MembershipPlan, pk=pk, is_active=True)
    
    def is_plan_in_use(self, plan):
        return plan.memberships.filter(status="active"    ).exists()
    
    def get(self, request, pk):
        plan = self.get_object(pk)
        serializer = MembershipPlanSerializer(plan)
        return Response(serializer.data)

    def put(self, request, pk):
        plan = self.get_object(pk)
        
        if self.is_plan_in_use(plan):
            return Response(
                {
                    "detail": "This plan is assigned to active members and cannot be updated."
                },
                status=status.HTTP_403_FORBIDDEN
            )


        serializer = MembershipPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        plan = self.get_object(pk)
        
        if self.is_plan_in_use(plan):
            return Response(
                {
                    "detail": "This plan is assigned to active members and cannot be updated."
                },
                status=status.HTTP_403_FORBIDDEN
            )


        serializer = MembershipPlanSerializer(
            plan,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        plan = self.get_object(pk)
        
        if self.is_plan_in_use(plan):
            return Response(
                {
                    "detail": "This plan is assigned to active members and cannot be updated."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        plan.delete()

        return Response(
            {"detail": "Membership plan deleted"},
            status=status.HTTP_204_NO_CONTENT
        )