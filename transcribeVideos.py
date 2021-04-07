import boto3
import uuid
import requests
import argparse
import os
from transcribe.srtUtils import *
from transcribe.transcribeUtils import *
import time
from os import listdir
from os.path import isfile, join

ROOT_DIR = os.path.abspath(os.curdir)

# Get the command line arguments and parse them
parser = argparse.ArgumentParser( prog='transcribeVideos.py', description='Upload all vids in a directory to S3 and transcribe them')
parser.add_argument('-region', required=True, help="The AWS region containing the S3 buckets" )
parser.add_argument('-bucket', required=True, help='The S3 bucket to put the videos to')
args = parser.parse_args()

# Example: python transcribeVideos.py -region us-east-1 -bucket videostoconvertjev/


def uploadVideoToS3( bucket, mediaFile, newName):

    s3 = boto3.resource('s3')

    response = s3.meta.client.upload_file(mediaFile, bucket , newName)

    return response

def transcribeVideo (region, inbucket, infile): 
    print(region, inbucket, infile)
    response = createTranscribeJob( region, inbucket, infile )
    print( "\n==> Transcription Job: " + response["TranscriptionJob"]["TranscriptionJobName"] + "\n\tIn Progress"),

    while( response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
            print( "."),
            time.sleep( 10 )
            response = getTranscriptionJobStatus( response["TranscriptionJob"]["TranscriptionJobName"] )

    print( "\nJob Complete")
    print( "\tStart Time: " + str(response["TranscriptionJob"]["CreationTime"]) )
    print( "\tEnd Time: "  + str(response["TranscriptionJob"]["CompletionTime"]) )
    print( "\tTranscript URI: " + str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) )

# Now get the transcript JSON from AWS Transcribe
    transcript = getTranscript( str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) ) 
# print( "\n==> Transcript: \n" + transcript)

# Create the SRT File for the original transcript and write it out.  
    writeTranscriptToSRT( transcript, 'en', ROOT_DIR + '/subtitles/' + fileToProcess + "_subtitles-en.srt" )  

# createVideo( args.infile, "subtitles-en.srt", args.outfilename + "-en." + args.outfiletype, "audio-en.mp3", True)
files = [f for f in listdir('./vids_to_process') if isfile(join('./vids_to_process', f))]

for fileToProcess in files:
    uploadVideoToS3(args.bucket, './vids_to_process/' + fileToProcess, fileToProcess.replace(" ", "_"))
    transcribeVideo(args.region, args.bucket, fileToProcess)


# cd src
# python transcribevideo.py -region us-east-1 -inbucket $awsinbucket -infile $infile
# cd ..

