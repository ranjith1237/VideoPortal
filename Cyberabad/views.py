import subprocess
import os
import datetime
import filetype
import requests
from requests.exceptions import HTTPError
from django.core.cache import cache
from django.http import JsonResponse
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.paginator import Paginator
from .models import Video,gps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import VideoForm
# ffmpeg tools
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
# celery tasks
from .tasks import chunk_Video_data,email,getLocations
# Email
from django.core.mail import send_mail
from celery import group
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@login_required()
def upload_Video(request):
    form= VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        video_Saved = form.save()
        tempPath = os.path.join(settings.BASE_DIR,'media/data')
        gpsData = os.path.join(settings.BASE_DIR,'media')
        gps_filePath = os.path.join(gpsData,str(video_Saved.sensorfile))
        thumbnail_path = os.path.join(tempPath,str(video_Saved.pk))
        os.mkdir(thumbnail_path)
        videoPath = os.path.join(settings.BASE_DIR,'media',str(video_Saved.videofile))
        chunk_Video_data.delay(videoPath,thumbnail_path,video_Saved.pk)
        getLocations.delay(gps_filePath,video_Saved.pk)
    context = {
        'form':form
    }
    return render(request, 'upload.html', context)

@login_required()
def all_Videos(request):
    allVideos = Video.objects.all()
    paginator = Paginator(allVideos, 8) 

    page = request.GET.get('page')
    page_videos = paginator.get_page(page)
    pageVideos = [page_videos[x:x+4] for x in range(0, len(page_videos), 4)]
    context = {
        'allVideos':page_videos,
        'pageVideos':pageVideos
    }
    return render(request,'videos.html',context)

@login_required()
def display_Video(request, id):
    try:
        singleVideo = Video.objects.get(pk=id)
        gpsData=gps.objects.filter(video=singleVideo).order_by('frameStamp')
    except ObjectDoesNotExist:
        messages.error(request, 'video doesnt exist')
        return HttpResponse("<h1>404 error</h1>")
    videoFP = os.path.join(settings.BASE_DIR,'media',str(singleVideo.videofile))
    latlng = [[float(gpsPt.position.latitude),float(gpsPt.position.longitude)] for gpsPt in gpsData]
    fExtension = "mp4"
    clip = VideoFileClip(videoFP)
    context={
        'id':id,
        'videofile':singleVideo,
        'gps':[(gpsData[0].position.latitude,gpsData[0].position.longitude)],
        'gpsPts':latlng,
        'startTime':'0',
        'endTime':str(clip.duration)
    }
    if request.method == "POST":
        timerange = request.POST.get('timerange')
        timerange = timerange.split("-")
        sTime = timerange[0].split(":")[1]
        eTime = timerange[1].split(":")[1]
        file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H:%I:%S') +"."+str(fExtension)
        folder_path = os.path.join(settings.BASE_DIR,'media','data','downloads')
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        file_path = os.path.join(folder_path,file_name)
        ffmpeg_extract_subclip(videoFP,float(sTime),float(eTime),targetname=file_path)
        context['startTime']=sTime
        context['endTime']=eTime
        file_wrapper = FileWrapper(open(file_path, 'rb'))
        file_mimetype = 'video/mp4'
        response = HttpResponse(file_wrapper, content_type=file_mimetype )
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response
    return render(request,'video.html',context)


def rithish(request):
    payload={
        'id':8
    }
    video_path = os.path.join(settings.BASE_DIR,'media','data',str(payload['id']))
    chunks=0
    for li in os.listdir(video_path):
        if li.endswith(".ts"):
            chunks+=1
    payload['chunks']=chunks
    print(payload)
    response=requests.post('http://10.4.16.53:9000/newVideo/',payload)
    if response.status_code==200:
        print("working")
        print(response.json())
    print(response.text)
    return HttpResponse("<h1>{{response.text}}</h1>")


@csrf_exempt
@api_view(['POST'])
def sendMedia(request):
    id = request.POST.get('id',1)
    if request.method=='POST':
        data=request.POST.get('data','gps')
        if data=='gps':
            singleVideo = Video.objects.get(pk=id)
            file_name = str(singleVideo.sensorfile)
            folder_path = os.path.join(settings.BASE_DIR,'media')
            file_path = os.path.join(folder_path,file_name)
            print("file path ",file_path)
            file_wrapper = FileWrapper(open(file_path, 'rb'))
            file_mimetype = 'text/plain'
            response = HttpResponse(file_wrapper, content_type=file_mimetype )
            response['Content-Length'] = os.stat(file_path).st_size
            response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
            return response
        chunk = request.POST.get('chunk',0)
        file_name='output'+str(chunk)+'.ts'
        folder_path = os.path.join(settings.BASE_DIR,'media','data',str(id))
        file_path = os.path.join(folder_path,file_name)
        file_wrapper = FileWrapper(open(file_path, 'rb'))
        file_mimetype = 'video/ts'
        response = HttpResponse(file_wrapper, content_type=file_mimetype )
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response


@login_required()
@api_view(['POST'])
def getGPS(request):
    gps_time=request.POST.get('time',1)
    video_id=request.POST.get('id',1)
    frame = float(gps_time)
    singleVideo = Video.objects.get(pk=video_id)
    gpsData=gps.objects.filter(video=singleVideo).order_by('frameStamp')
    latlng = [[float(gpsPt.position.latitude),float(gpsPt.position.longitude)] for gpsPt in gpsData]
    return JsonResponse({
                'gpsPts':latlng,
                'position':str(gpsData[int(frame)].position),
                'address':gpsData[int(frame)].address
            })