from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from Cyberabad.models import Video
from django.core.paginator import Paginator

from . import forms

class SignUp(generic.CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


@login_required()
def uploadedVideos(request):
    allVideos = Video.objects.filter(user=request.user)
    paginator = Paginator(allVideos, 8)

    page = request.GET.get('page')
    page_videos = paginator.get_page(page)
    pageVideos = [page_videos[x:x+4] for x in range(0, len(page_videos), 4)]
    context = {
        'allVideos':page_videos,
        'pageVideos':pageVideos
    }
    return render(request,'videos.html',context)