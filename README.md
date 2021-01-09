# converter
# (documentation outdated)

Script to maintain a multimedia library. It will make sure that the codec and bitrate that each file has is the expected and it will do the transcodding if needed.

It can eficiently handle libraries with more than 100.000 multimedia files automatically.
I was no able to find a free/paid software that allows me to do that, so I made my own :)

**Requisites:**
- ffmpeg
- redis server
- python3
- pip3 modules: bs4, redis, colorama, argparse

**Configuration:**

* Change de following files as needed:

conf.py:
```python3
# redis server host
REDIS_HOST = '10.0.0.3'

# Multimedia library path
LIBRARY = '/XXXX/YYYYY/ZZZZZZ'

# Temporal folder to save finished transcodding and ongoing ones
TEMPORAL = '/XXXX/YYYYY/ZZZZZZ'
```

parse.py:
```python3
probe = 'ffprobe -v quiet -print_format json -show_streams'
aria = 'aria2c --disable-ipv6=true --follow-torrent=mem --seed-time=0 --enable-color=false --check-certificate=false --console-log-level=error --summary-interval=0'
ffmpeg = 'ffmpeg -hide_banner -y'
ffmpeg_vo = '-vsync 2 -r 30 -vf scale=1280x1280:force_original_aspect_ratio=decrease -b:v 500k -movflags +faststart'

# Commands used
cmds = {
    # To get coddecs details about a file
    'w-probe': '%s {0}' % probe,
    # To transcode a video file using nvidia hardware aceleration
    'w-hvideo': '%s -hwaccel nvdec -i {0} -c:a copy -c:v h264_nvenc %s -f mp4 {1}' % ( ffmpeg, ffmpeg_vo ),
    # To transcode a video file using the cpu
    'w-svideo': '%s -i {0} -c:a copy -c:v h264 %s -f mp4 {1}' % ( ffmpeg, ffmpeg_vo ),
    # To transcode the audio of a video file
    'w-vaudio': '%s -i {0} -c:a aac -b:a 100k -c:v copy -f mp4 {1}' % ( ffmpeg ),
    # To transcode an audio file
    'w-audio': '%s -i {0} -c:a mp3 -b:a 128k -f mp3 {1}' % ( ffmpeg ),
    # To download a file
    'w-download': '%s -d / -o {1} {0}' % aria,
    # To download a torrent
    'w-torrent': '%s -d {1} {0}' % aria
}

# This function makes sure that the file's coddecs are correct.
# If you have a different needs, you should change this one it too.
def job_codec(f, codecs):
    (...)
```

**Usage:**

```bash
# To print a detailed usage text:
./main -h

# To scan files in the library and create jobs to analize them if needed:
./main -s

# To analize and transcode the files if needed:
./main -k w-download,w-torrent,w-svideo,w-vaudio,w-audio

# To transcode the files using the GPU you may notice
# that there is a maximum supported number of transcodding jobs that they can run in parallel.
# You can match that amount use the parameter '-jN' as needed.
# By default, all the videos are transcodded using the GPU.
./main -j2 -k w-hvideo

# To force retry some jobs, you can clean the redis lists 'done', 'doing' and 'failed'
# using the command:
./main -p
```

**Logs:**

Executed commands output is appended to: **$TEMP/converter.out**
