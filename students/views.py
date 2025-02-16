from .models import *
from .serializers import *
from django.contrib.auth.hashers import make_password,check_password
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken,TokenError
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render

def index(request):
    student = Student.objects.values_list("full_name", "student_class__name")
    return render(request,'students/index.html',{
        "student": student
    })

def custom_404_view(request, exception):
    return render(request, "students/404.html", status=404)

class LoginStudent(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = Student.objects.get(username=username)
            
            if check_password(password,user.password):
                refresh_token = RefreshToken()
                refresh_token["id"] = user.pk
                refresh_token["username"] = user.username
                access_token = refresh_token.access_token

                return Response({
                    'access':str(access_token),
                    'refresh':str(refresh_token)
                })
            
            else: 
                return Response({
                    'error':'Tên đăng nhập hoặc mật khẩu không đúng'
                },status=status.HTTP_400_BAD_REQUEST)
            
        except Student.DoesNotExist:
            return Response({
                'error':'Tên đăng nhập hoặc mật khẩu không đúng'
            }, status=status.HTTP_401_UNAUTHORIZED)
        

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get('id')
            if not user_id:
                raise InvalidToken("Token Thông Báo Không có ID trên")
            
            user = Student.objects.get(id=user_id)
            return user
        except Student.DoesNotExist:
            raise InvalidToken("User Không Tồn Tại")
        
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        serializer = StudentSerializer(request.user)
        return Response({
            "message": "Lấy Thông Tin Students Thành Công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)