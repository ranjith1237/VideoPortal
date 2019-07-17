import os
from django.db import models
from django.utils.timezone import now
from geoposition.fields import GeopositionField
from django.contrib.auth.models import User


class Video(models.Model):
    name =  models.CharField(max_length=500)
    captured_time = models.DateTimeField(default=now,null=False, verbose_name="Captured Time(YYYY-MM-DD HH:MM:SS)")
    uploaded_on = models.DateTimeField(default=now)
    videofile = models.FileField(upload_to='data/', null=False, verbose_name="Video")
    sensorfile = models.FileField(upload_to="gps/",null=True,verbose_name="Gps sensor(.json)")
    routemaps = models.FileField(upload_to="routes/",null=True,verbose_name="Route map (.png,.jpeg)")
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    def __str__(self):
        return self.name + ": " + str(self.videofile)

class gps(models.Model):
    position = GeopositionField()
    frameStamp = models.DateTimeField(default=now)
    address    = models.CharField(max_length=1500)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.position)+ " : "+ str(self.frameStamp)+ " : " + str(self.address)

class comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    video = models.ForeignKey(Video, on_delete=models.CASCADE,null=True)
    commented_on = models.DateTimeField(default=now)
    comment = models.CharField(max_length=5000)
    def __str__(self):
        return self.content+":"+str(self.commented_on)