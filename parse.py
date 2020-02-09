import re
import os
import json
import math
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

term, conf = None, None
regex_gitir_cdn = re.compile(r"^https://cdn[0-9]*.git.ir/")
regex_path = re.compile(r"[^\w\-_\. ]")

probe     = 'ffprobe -v quiet -print_format json -show_streams'
aria      = 'aria2c --disable-ipv6=true --follow-torrent=mem --seed-time=0 --enable-color=false --check-certificate=false --console-log-level=error --summary-interval=0'
ffmpeg    = 'ffmpeg -hide_banner -y'
ffmpeg_vo = '-vsync 2 -r 30 -vf scale=1280x1280:force_original_aspect_ratio=decrease -b:v 500k -movflags +faststart'

cmds = {
    'w-probe'   : '%s             {0}' % probe,
    'w-download': '%s -d / -o {1} {0}' % aria,
    'w-torrent' : '%s -d      {1} {0}' % aria,
    'w-hvideo'  : '%s -hwaccel nvdec -i {0} -c:a copy           -c:v h264_nvenc %s -f mp4 {1}' % ( ffmpeg, ffmpeg_vo ),
    'w-svideo'  : '%s                -i {0} -c:a copy           -c:v h264       %s -f mp4 {1}' % ( ffmpeg, ffmpeg_vo ),
    'w-vaudio'  : '%s                -i {0} -c:a aac  -b:a 100k -c:v copy          -f mp4 {1}' % ( ffmpeg ),
    'w-audio'   : '%s                -i {0} -c:a mp3  -b:a 128k                    -f mp3 {1}' % ( ffmpeg )
}

for i in cmds:
    cmds[i] = re.sub(' +', ' ', cmds[i]).split(' ')


def init(t, c):
    global term, conf
    term, conf = t, c


def git_url(url):
    soup = BeautifulSoup( urlopen(url), features="html.parser" )
    
    title = soup.find( 'span', { "class": "en-style en-title" } ).contents[0]
    title = regex_path.sub('', title)
    
    links = [ x.get('href') for x in soup.findAll( 'a', attrs={'href': regex_gitir_cdn} ) ]

    return [ ('%s/%s' % (title, os.path.basename(urlparse(l).path)), l) for l in links ]


def job_codec(f, codecs):
    audio, video = None, None
    
    for c in codecs:
        if len(c) < 3:
            term.out('inv_probe', f)
        elif c[0] == 'audio':
            audio = (c[1], c[2])
        elif c[0] == 'video' and c[1] not in ['mjpeg', 'png']:
            video = (c[1], c[2])
    
    if video:
        if video[0] != 'h264' or not video[1].isnumeric() or int(video[1]) > 600000:
            term.out('new_hvideo', f)
            return 'w-hvideo'
        
        if audio and (audio[0] != 'aac' or int(audio[1]) > 129000):
            term.out('new_vaudio', f)
            return 'w-vaudio'
    elif audio:
        if audio[0] != 'mp3' or not audio[1].isnumeric() or int(audio[1]) > 129000:
            term.out('new_audio', f)
            return 'w-audio'

    return None


def job_probe(f, p):
    codecs = [ x.split(';') for x in p.split('|')[1].split('#') ]

    return job_codec(f, codecs)


def redis_pop(pop):
    if not pop:
        return None, None, None, None

    jobId, order = pop
    tmp = order.split('|')
    job = tmp[-1]
    dest = tmp[0]

    if jobId == 'w-download':
        dest = os.path.join(conf.DONE_PATH, dest)
    elif jobId == 'w-torrent':
        dest = conf.DONE_PATH
    else:
        dest = os.path.join(conf.DONE_PATH, job)
        job = os.path.join(conf.LIBRARY, job)

    return jobId, job, dest, '%s|%s' % (jobId, order)


def probe_out(job, output):
    js = json.loads(''.join(output))
    time = math.floor( os.stat(job).st_mtime )
    codecs = [ ( i.get('codec_type',''), i.get('codec_name', ''), i.get('bit_rate', '') ) for i in js['streams'] ]
    codecs_txt = '#'.join( [ '%s;%s;%s' % (i[0], i[1], i[2]) for i in codecs ] )
    probe_txt = '%s|%s' % ( time, codecs_txt )
    key = os.path.relpath(job, conf.LIBRARY)

    return (key, probe_txt, job_codec(key, codecs))


def cmd(jobId, *params):
    res = []

    for i in cmds[jobId]:
        v = params[int( i[1:-1] )] if i[0] == '{' and  i[-1] == '}' else i
        res.append( v )

    return res

