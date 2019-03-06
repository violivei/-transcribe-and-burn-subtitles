# AWS Transcribe and FFMPEG burning of subtitles

This tool will take a video:

1. Transcribe it using AWS
2. Allow you to proof read and edit the result
3. Burn the subtitles into a video using FFMPEG.

This is useful for sites like Facebook or LinkedIn where the audio doesn't auto play but you want to grab the viewer's attention.

This is a heavy modification/simplification on this lovely repository: https://github.com/aws-samples/aws-transcribe-captioning-tools

## Get the transcription

1. Create an S3 bucket for your input videos and the output videos
2. Put the videos you want to translate into the `vids_to_process` dir.
3. Run `transcribeVideos.py`

## Edit it

1. Edit the generated subtitles in the `subtitles` dir

## Build the video

1. Run `pip install -r requirements.txt`
1. Run the `burnSubtitles.py` script. It requires you have docker up and running

