from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('password_reset/', views.SignUp.as_view(), name='signup'),
    path('uploaded/',views.uploadedVideos,name='uploaded'),
]