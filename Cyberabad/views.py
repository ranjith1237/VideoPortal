import subprocess
import os
import datetime
import filetype
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.paginator import Paginator
from .models import Video
from .forms import VideoForm
# ffmpeg tools
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

def upload_Video(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')
    form= VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        video_Saved = form.save()
        if request.user:
            tempPath = os.path.join(settings.BASE_DIR,'media/data',str(request.user.id))
            if not os.path.exists(tempPath):
                os.mkdir(tempPath)
            video_Saved = form.save()
            thumbnail_path = os.path.join(tempPath,str(video_Saved.pk))
            os.mkdir(thumbnail_path)
            videoFP = os.path.join(settings.BASE_DIR,'media',str(video_Saved.videofile))
            clip = VideoFileClip(videoFP)
            clip.save_frame(thumbnail_path+"/thumbnail.jpg",t=(clip.duration)/2)
    context = {
        'form':form
    }
    return render(request, 'upload.html', context)

def all_Videos(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')
    allVideos = Video.objects.all()
    paginator = Paginator(allVideos, 1) # Show 3 videos per page

    page = request.GET.get('page')
    page_videos = paginator.get_page(page)
    context = {
        'allVideos':page_videos,
    }
    return render(request,'videos.html',context)

def display_Video(request, id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('/accounts/login')
    print("single video id  ",id)
    singleVideo = Video.objects.get(pk=id)
    videoFP = os.path.join(settings.BASE_DIR,'media',str(singleVideo.videofile))
    fExtension = "mp4"
    clip = VideoFileClip(videoFP)
    context={
        'videofile':singleVideo,
        'startTime':'0',
        'endTime':str(clip.duration)
    }
    if request.method == "POST":
        timerange = request.POST.get('timerange')
        timerange = timerange.split("-")
        sTime = timerange[0].split(":")[1]
        eTime = timerange[1].split(":")[1]
        file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H:%I:%S') +"."+str(fExtension)
        folder_path = os.path.join(settings.BASE_DIR,'media','data',str(request.user.id),'downloads')
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