import subprocess
from celery import shared_task
from moviepy.editor import VideoFileClip


@shared_task()
def chunk_Video_data(videoPath,outputPath):
    print("videoPAth$$$$$$$$$$    ",videoPath)
    cmd="ffmpeg -i "+videoPath+" -b:v 1M -g 60 -hls_time 100 -hls_list_size 0 -hls_segment_size 50000 "+outputPath+"/output.m3u8"
    subprocess.call(cmd,shell=True)

@shared_task()
def generate_thumbnail(videoPath,thumbnail_path):
    print("videoPAth$$$$$$$$$$===========>\n\n\n    ",videoPath)
    clip = VideoFileClip(videoPath)
    clip.save_frame(thumbnail_path+"/thumbnail.jpg",t=(clip.duration)/2)
