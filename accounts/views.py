import os
import shutil
import logging
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from Cyberabad.models import Video,gps
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.conf import settings
from . import forms

logger = logging.getLogger(__name__)


class SignUp(generic.CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

@login_required()
def uploadedVideos(request):
    allVideos = Video.objects.filter(user=request.user)
    paginator = Paginator(allVideos, 4)

    page = request.GET.get('page')
    page_videos = paginator.get_page(page)
    context = {
        'allVideos':page_videos
    }
    return render(request,'uploaded.html',context)


@login_required()
@api_view(['POST'])
def removeMedia(request):
    id=request.POST.get("id")
    videoInst=Video.objects.get(pk=id)
    gpsInst=gps.objects.filter(video=videoInst)
    if len(gpsInst) > 0:
        gpsInst.delete()
    videoFile = videoInst.videofile
    sensorFile = videoInst.sensorfile
    routemap = videoInst.routemaps
    videoInst.delete()
    videoFilePath = os.path.join(settings.BASE_DIR,'media',str(videoFile))
    sensorFilePath = os.path.join(settings.BASE_DIR,'media',str(sensorFile))
    routemapPath = os.path.join(settings.BASE_DIR,'media',str(routemap))
    chunksFolderPath = os.path.join(settings.BASE_DIR,'media','data',str(id))
    try:
        os.remove(videoFilePath)
    except:
        logger.exception("Video file is not present at ",videoFilePath)
    try:
        os.remove(sensorFilePath)
    except:
        logger.exception("Sensor file is not present at ",sensorFilePath)
    try:
        os.remove(routemapPath)
    except:
        logger.exception("route map is not present at ",routemapPath)
    try:
        shutil.rmtree(chunksFolderPath)
    except:
        logger.exception("folder is not present at ",chunksFolderPath)

    return JsonResponse({
            "id":id,
            'success':True,
            'message':"successfully deleted "+videoInst.name,
        })