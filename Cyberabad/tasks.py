from __future__ import absolute_import, unicode_literals
import os
import subprocess
import requests
import json
from celery import shared_task
from celery import task
from moviepy.editor import VideoFileClip
from django.core.mail import send_mail,EmailMultiAlternatives,get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
from .models import Video,gps
from .models import gps as GeoPosition
from celery.decorators import periodic_task
from datetime import timedelta
import pytz
import logging

logger = logging.getLogger(__name__)


def violation(id):
    payload={
		'id':id,
		'data':'video'
	}
    video_path = os.path.join(settings.BASE_DIR,'media','data',str(payload['id']))
    chunks=0
    for li in os.listdir(video_path):
        if li.endswith(".ts"):
            chunks+=1
    payload['chunks']=chunks
    try:
        response=requests.post('http://10.4.16.53:9000/newVideo/',payload)
        if response.status_code==200:
            logger.debug("working")
        logger.debug(response.text)
        return "working"
    except:
        logger.exception("failure in connecting to violation portal")
    return "failed"

@shared_task()
def chunk_Video_data(videoPath,outputPath,id):
    cmd="ffmpeg -i "+videoPath+" -profile:v baseline -level 3.0 -s 1920x1080 -start_number 0 -hls_list_size 0 -f hls "+outputPath+"/output.m3u8"
    subprocess.call(cmd,shell=True)
    clip = VideoFileClip(videoPath)
    clip.save_frame(outputPath+"/thumbnail.jpg",t=(clip.duration)/2)
    violation(id)

@shared_task()
def email():
    subject = 'Thank you for registering to our site'
    message = 'a new video has been uploaded'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['ranjithreddy1061995@gmail.com']
    send_mail( subject, message, email_from, recipient_list )

def gpsCoordinates(gps_filePath):
	gpsList = []
	with open(gps_filePath) as textfile:
		lines = textfile.readlines()
		lines=lines[1:]
		for line in lines:
			features_row = line.split(',')
			gpsList.append({'lat':features_row[6],"lng":features_row[7],"timeStamp":features_row[0][:10]})
	return gpsList

def getTime(timestamp):
	tz = pytz.timezone(settings.TIME_ZONE)
	dt_object = datetime.fromtimestamp(timestamp)
	return dt_object.astimezone(tz)

@shared_task()
def getLocations(gps_filePath,id):
	http_proxy  = "http://proxy.iiit.ac.in:8080"
	https_proxy = "https://proxy.iiit.ac.in:8080"
	proxyDict = {
              "http"  : http_proxy, 
              "https" : https_proxy
            }
	gpsList = gpsCoordinates(gps_filePath)
	videoInst = Video.objects.get(pk=id)
	for i in range(0,len(gpsList)):
		dateTime = getTime(int(gpsList[i]["timeStamp"]))
		latlng=gpsList[i]["lat"]+","+gpsList[i]["lng"]
		if i%15==0:
			url = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+latlng+"&key="+settings.GEOPOSITION_GOOGLE_MAPS_API_KEY
			r=requests.get(url,proxies=proxyDict)
			addrs = json.loads(r.text)
			formatted_address =  addrs["results"][0]["formatted_address"]
		else:
			latestgps = gps.objects.filter(video=videoInst).order_by('-pk')
			print("latestgps====> ",latestgps)
			formatted_address = latestgps[0].address
		strDT=str(dateTime)
		
		p=GeoPosition(position=(latlng),frameStamp=strDT,address=formatted_address)
		p.video=videoInst
		p.save()
	payload={
		'id':id,
		'data':'gps'
	}
	try:
		requests.post('http://10.4.16.53:9000/newVideo/',payload)
	except:
		logger.exception("not working")

@periodic_task(run_every=timedelta(minutes=1))
def send_periodic_email():
	with open('./Cyberabad/data/recipients_users.json') as f:
		other_users=json.load(f)
		recipients=other_users["recipients"]
	subject, from_email, to = '[test email] Video Capture Update', settings.EMAIL_HOST_USER, 'ranjithreddy1061995@gmail.com'
	allVideos = Video.objects.all()
	html_content = render_to_string('mail_template.html', {'allVideos':allVideos})
	text_content = strip_tags(html_content)
	msg = EmailMultiAlternatives(subject, text_content, from_email, [to],cc=recipients)
	msg.attach_alternative(html_content, "text/html")
	msg.send()