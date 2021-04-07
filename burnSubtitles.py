import os
import subprocess
import argparse
import docker
import string

parser = argparse.ArgumentParser( prog='burnSubtitles.py', description='Burn the subtitles into the video')
parser.add_argument('-videofile', required=True, help='The video file to use' )
parser.add_argument('-subtitlefile', required=True, help='Subtitle file')
parser.add_argument('-outputfile', required=True, help='Filename of the output videofile')
parser.add_argument('-alignment', type=int, required=True)
parser.add_argument('-font_colour', type=str, required=True)
parser.add_argument('-background_colour', type=str, required=True)
args = parser.parse_args()
print("DASDSADSAD")
print(args)
# subprocess.call(['C:\\Temp\\a b c\\Notepad.exe', 'C:\\test.txt'])

# docker run -v $PWD:/tmp/ -t ffmpegfonts -stats -i /tmp/$infile \
#   -vf subtitles=/tmp/subtitles-en.srt:force_style='FontName=TakaoPGothic' -f mp4 /tmp/$outfile

client = docker.from_env()

print("Building docker image")
ffmpegImage = client.images.build(dockerfile='Dockerfile', path='.')[0]

print("Running docker image")
force_style = string.Template("FontName=Amazon Ember,"
                                f"Alignment={args.alignment},"
                                f"PrimaryColour={args.font_colour},"
                                f"OutlineColour={args.background_colour}")
print(force_style.template)
command =  """-i /tmp/%s -vf subtitles="f=/tmp/%s:fontsdir=/tmp:force_style='%s'" -f mp4 /tmp/%s""" % (args.videofile, args.subtitlefile, force_style.template, args.outputfile)

cwd = os.getcwd()
vol =['%s:/tmp' % cwd]
response = client.containers.run(ffmpegImage, command, volumes=vol)
print(response)
