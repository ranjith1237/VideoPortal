import os
from django.db import models
from django.utils.timezone import now


class Video(models.Model):
    name= models.CharField(max_length=500)
    pub_date = models.DateField(default=now)
    videofile= models.FileField(upload_to='data/', null=True, verbose_name="")

    def __str__(self):
        return self.name + ": " + str(self.videofile)