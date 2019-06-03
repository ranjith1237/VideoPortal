import os
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
        print("########")
        response=requests.post('http://10.4.16.53:9000/newVideo/',payload)
        if response.status_code==200:
            print("working")
        print(response.text)
        return "working"
    except:
        print("failure in connecting to violation portal")
    return "failed"

@shared_task()
def chunk_Video_data(videoPath,outputPath,id):
    cmd="ffmpeg -i "+videoPath+" -profile:v baseline -level 3.0  -start_number 0 -hls_list_size 0 -f hls -vcodec copy "+outputPath+"/output.m3u8"
    subprocess.call(cmd,shell=True)
    clip = VideoFileClip(videoPath)
    clip.save_frame(outputPath+"/thumbnail.jpg",t=(clip.duration)/2)
    print("done")
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
	'''gpsList = gpsCoordinates(gps_filePath)
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
		p.save()'''
	payload={
		'id':id,
		'data':'gps'
	}
	try:
		requests.post('http://10.4.16.53:9000/newVideo/',payload)
	except:
		print("not working")