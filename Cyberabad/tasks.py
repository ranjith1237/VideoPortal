import subprocess
import requests
import json
from celery import shared_task
from moviepy.editor import VideoFileClip
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from .models import Video,gps
from .models import gps as GeoPosition
import pytz


@shared_task()
def chunk_Video_data(videoPath,outputPath):
    cmd="ffmpeg -i "+videoPath+" -b:v 1M -g 60 -hls_time 100 -hls_list_size 0 -hls_segment_size 1000000 "+outputPath+"/output.m3u8"
    subprocess.call(cmd,shell=True)
    clip = VideoFileClip(videoPath)
    clip.save_frame(outputPath+"/thumbnail.jpg",t=(clip.duration)/2)

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
	gpsList = gpsCoordinates(gps_filePath)
	for gps in gpsList:
		latlng=gps["lat"]+","+gps["lng"]
		dateTime = getTime(int(gps["timeStamp"]))
		url = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+latlng+"&key="+settings.GEOPOSITION_GOOGLE_MAPS_API_KEY
		r=requests.get(url)
		addrs = json.loads(r.text)
		formatted_address =  addrs["results"][0]["formatted_address"]
		strDT=str(dateTime)
		videoInst = Video.objects.get(pk=id)
		p=GeoPosition(position=(latlng),frameStamp=strDT,address=formatted_address)
		p.video=videoInst
		p.save()