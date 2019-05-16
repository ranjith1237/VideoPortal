import os
from django.db import models
from django.utils.timezone import now
from geoposition.fields import GeopositionField



class Video(models.Model):
    name =  models.CharField(max_length=500)
    captured_time = models.DateTimeField(default=now,null=False, verbose_name="YYYY-MM-DD HH:MM:SS")
    uploaded_on = models.DateTimeField(default=now)
    videofile = models.FileField(upload_to='data/', null=False, verbose_name="Video")
    sensorfile = models.FileField(upload_to="gps/",null=True,verbose_name="Gps sensor(.txt)")
    routemaps = models.FileField(upload_to="routes/",null=True,verbose_name="Route map (.png,.jpeg)")
    def __str__(self):
        return self.name + ": " + str(self.videofile)

class gps(models.Model):
    position = GeopositionField()
    frameStamp = models.DateTimeField(default=now)
    address    = models.CharField(max_length=1500)
    def __str__(self):
        return str(self.position)+ " : "+ str(frameStamp)