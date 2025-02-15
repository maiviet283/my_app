from django.urls import path
from . import views

app_name = 'students'
urlpatterns = [
    path('', views.index, name='index'),
    path('api/login/user', views.LoginStudent.as_view(), name='login_user'),
    path('api/details/user', views.UserDetailView.as_view(), name='user_detail'),
]
