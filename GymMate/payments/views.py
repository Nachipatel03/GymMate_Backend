from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import PaymentCreateSerializer

# Create your views here.
class CreatePaymentAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response({
            "message": "Payment successful & membership activated"
        }, status=201)