from django import forms
from .models import Video,comments

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields= ["name","captured_time", "videofile","sensorfile","routemaps"]

class commentForm(forms.ModelForm):
    class Meta:
        model = comments
        fields = ["comment"]
        widgets = {
            'comment': forms.TextInput(attrs={'class': 'form-control','placeholder':'leave a comment...'})
        }