import os
import subprocess
import argparse
import docker
import string
import webvtt
import numpy as np
import pysrt
import math

def ceildiv(a, b):
    return int(math.ceil(a / float(b)))

def get_video_length(filename):

    output = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename)).strip()
    video_length = int(float(output))
    print("Video length in seconds: "+str(video_length))

    return video_length

parser = argparse.ArgumentParser( prog='burnSubtitles.py', description='Burn the subtitles into the video')
parser.add_argument('-videofile', required=True, help='The video file to use' )
parser.add_argument('-subtitlefile', required=True, help='Subtitle file')
parser.add_argument('-alignment', type=int, required=True)
parser.add_argument('-font_colour', type=str, required=True)
parser.add_argument('-background_colour', type=str, required=True)
parser.add_argument('-split_length', type=int, required=True)
args = parser.parse_args()

### RANDOMLY REMOVE SUBTITLES ###

ext = os.path.splitext(args.subtitlefile)[-1].lower()
randomly_generated_subtitles_filename = "{0}_{2}.{1}".format(*args.subtitlefile.rsplit('.', 1) + ["random"])
print(randomly_generated_subtitles_filename)

if ext == ".vtt":
    vtt = webvtt.read(args.subtitlefile)
    for caption in vtt:
        if np.random.random() > 0.5:
            vtt.captions.remove(caption)
    vtt.save(randomly_generated_subtitles_filename)
else:
    subs = pysrt.open(args.subtitlefile)
    for idx, caption in enumerate(subs):
        if np.random.random() > 0.5:
            del subs[idx]
    subs.save(randomly_generated_subtitles_filename, encoding='utf-8')

### BURNING SUBTITLES AND TRIMMING VIDEO ###

print("Building docker image")
client = docker.from_env()
ffmpegImage = client.images.build(dockerfile='Dockerfile', path='.')[0]

print("Running docker image")
force_style = string.Template("FontName=Amazon Ember,"
                                f"Alignment={args.alignment},"
                                f"PrimaryColour={args.font_colour},"
                                "FontSize=18,"
                                f"BackColour={args.background_colour},"
                                "BorderStyle=4,"
                                "Outline=0,"
                                "Shadow=0")
print(force_style.template)
command =  """-i /tmp/%s -vf subtitles="f=/tmp/%s:fontsdir=/tmp:force_style='%s'" """ % (args.videofile, randomly_generated_subtitles_filename, force_style.template)
print("Command: " + command)
try:
    filebase = ".".join(args.videofile.split(".")[:-1])
    fileext = args.videofile.split(".")[-1]
except IndexError as e:
    raise IndexError("No . in filename. Error: " + str(e))

video_length = get_video_length(args.videofile)
split_count = ceildiv(video_length, args.split_length)
for n in range(0, split_count):
    split_args = ""
    if n == 0:
        split_start = 0
    else:
        split_start = args.split_length * n

    split_args += "-ss " + str(split_start) + " -t " + str(args.split_length) +  " -copyts "
    split_args += command
    split_args += "-f mp4 /tmp/" + filebase + "-" + str(n+1) + "-of-" + str(split_count) + "." + fileext
            
    print("About to run: " + split_args)
    cwd = os.getcwd()
    vol =['%s:/tmp' % cwd]
    response = client.containers.run(ffmpegImage, split_args, volumes=vol)
    print(response)