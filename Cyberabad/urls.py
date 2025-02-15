from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'Cyberabad'
urlpatterns = [
    path('upload/',views.upload_Video,name='upload'),
    path('all/',views.all_Videos,name='allVideos'),
    path('<int:id>/',views.display_Video,name='singleVideo'),
    path('<int:id>/postcomment/',views.post_Comment,name="postComment"),
    path('<int:id>/editcomment/',views.edit_comment,name="editComment"),
    path('<int:id>/removecomment/',views.remove_comment,name="removeComment"),
    path('rithish/',views.rithish,name='newVideo'),
    path('sendMedia/',views.sendMedia,name='sendMedia'),
    path('location/',views.getGPS,name='location'),
]