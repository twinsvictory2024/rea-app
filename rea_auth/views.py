from django.contrib.auth import get_user_model, authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from knox.models import AuthToken
from .serializers.login import LoginSerializer
from .serializers.register import RegisterSerializer

User = get_user_model()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                _, token = AuthToken.objects.create(user)
                
                return Response(
                    {
                        "user": LoginSerializer(user).data,
                        "token": token
                    }
                )
            else:
                return Response({"error": "Invalid credentials"}, status=400)
        else:
            return Response(serializer.errors, status=400)
        
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            _, token = AuthToken.objects.create(user)
            
            return Response(
                {
                    "user": RegisterSerializer(user).data,
                    "token": token
                },
                status=201
            )
        else:
            return Response(serializer.errors, status=400)