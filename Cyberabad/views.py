import subprocess
import os
import datetime
import filetype
from django.core.cache import cache
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.db.models import ObjectDoesNotExist
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.paginator import Paginator
from .models import Video
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import VideoForm
# ffmpeg tools
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from .tasks import chunk_Video_data,generate_thumbnail
from celery import chain


@login_required()
def upload_Video(request):
    form= VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        video_Saved = form.save()
        if request.user:
            tempPath = os.path.join(settings.BASE_DIR,'media/data')
            video_Saved = form.save()
            thumbnail_path = os.path.join(tempPath,str(video_Saved.pk))
            os.mkdir(thumbnail_path)
            videoPath = os.path.join(settings.BASE_DIR,'media',str(video_Saved.videofile))
            job = chain(chunk_Video_data(videoPath,thumbnail_path),
                    generate_thumbnail(videoPath,thumbnail_path))
            job.delay()
    context = {
        'form':form
    }
    messages.success(request, 'Successfully uploaded video')
    return render(request, 'upload.html', context)


@login_required()
def all_Videos(request):
    allVideos = Video.objects.all()
    paginator = Paginator(allVideos, 1) 

    page = request.GET.get('page')
    page_videos = paginator.get_page(page)
    context = {
        'allVideos':page_videos,
    }
    return render(request,'videos.html',context)

@login_required()
def display_Video(request, id):
    try:
        singleVideo = Video.objects.get(pk=id)
    except ObjectDoesNotExist:
        messages.error(request, 'video doesnt exist')
        return HttpResponse("<h1>404 error</h1>")
    videoFP = os.path.join(settings.BASE_DIR,'media',str(singleVideo.videofile))
    fExtension = "mp4"
    clip = VideoFileClip(videoFP)
    context={
        'id':id,
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