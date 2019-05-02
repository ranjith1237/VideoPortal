from django import forms
from .models import Video
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields= ["name","captured_time", "videofile","sensorfile","routemaps"]