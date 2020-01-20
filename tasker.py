#!python3
import os
import glob
import math
import redis
import sys
import re
from urllib.request import urlopen
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from libs import Workers, Conf, Term, Executor

Term.out('header', 'Connecting to Redis...')
red = redis.StrictRedis( host=Conf.REDIS_HOST, decode_responses=True )
files = []

workers = Workers(Conf, Term, Executor, red)

def Downloads():
    Term.out('header', 'Creating download jobs...')

    regex_gitir_cdn = re.compile(r"^https://cdn[0-9]*.git.ir/")
    regex_gitir = re.compile(r"^https://git.ir/")
    regex_path = re.compile(r"[^\w\-_\. ]")

    torrent = []
    download = []

    for url in Term.args.urls:
        if regex_gitir.match(url):
            soup = BeautifulSoup( urlopen(url), features="html.parser" )
    
            title = soup.find( 'span', { "class": "en-style en-title" } ).contents[0]
            title = regex_path.sub('', title)
    
            links = [ x.get('href') for x in soup.findAll( 'a', attrs={'href': regex_gitir_cdn} ) ]
    
            for l in links:
                path = title + '/' + os.path.basename( urlparse(l).path )

                download.append(path + '|' + l)
                Term.out('new_download', l)
        else:
            torrent.append(url)
            Term.out('new_download', url)
    
    red.rpush('w-torrent',  *torrent)  if len(torrent)  else None
    red.rpush('w-download', *download) if len(download) else None


def Scan():
    Term.out('header', 'Scanning files...')

    for i in glob.glob(os.path.join(Conf.LIBRARY, '**', '*.*'), recursive=True):
        if os.path.splitext(i)[1].lower() in Conf.ALL_EXTS:
            files.append( ( math.floor( os.stat(i).st_mtime ), os.path.relpath( i, Conf.LIBRARY )))


def ResetJobs():
    Term.out('header', 'Resetting jobs...')

    red.delete('w-probe', 'w-hvideo', 'w-svideo', 'w-audio', 'w-vaudio')


def SyncProbes():
    Term.out('header', 'Syncing probes...')

    probes = red.hgetall('probes')
    probes_rm = []
    probes_jobs = []

    for i in files:
        t, f = i

        inProbes = f in probes
        changed = inProbes and probes[f].split('|')[0] != str(t)
    
        if not inProbes or changed:
            probes_jobs.append(f)
            Term.out('new_probe', f)

        if changed:
            probes_rm.append(f)
    
    red.hdel('probes',   *probes_rm)   if len(probes_rm)   else None
    red.rpush('w-probe', *probes_jobs) if len(probes_jobs) else None


def SyncJobs():
    Term.out('header', 'Syncing jobs...')

    probes = red.hgetall('probes')
    hvideo, vaudio, audio = [], [], []

    for f, v in probes.items():
        codecs = [x.split(';') for x in probes[f].split('|')[1].split('#')]
        audio, video = None, None
    
        for c in codecs:
            if len(c) < 3:
                Term.out('inv_probe', f)
            elif c[0] == 'audio':
                audio = (c[1], c[2])
            elif c[0] == 'video' and c[1] not in ['mjpeg', 'png']:
                video = (c[1], c[2])
    
        if video:
            if video[0] != 'h264' or video[1] == 'null' or (video[1] != 'null' and int(video[1]) > 600000):
                hvideo.append(f)
                Term.out('new_hvideo', f)
            elif audio and (audio[0] != 'aac' or int(audio[1]) > 129000):
                vaudio.append(f)
                Term.out('new_vaudio', f)
        elif audio:
            if audio[0] != 'mp3' or audio[1] == 'null' or int(audio[1]) > 129000:
                audio.append(f)
                Term.out('new_audio', f)
    
    red.rpush('w-hvideo', *hvideo) if len(hvideo) else None
    red.rpush('w-vaudio', *vaudio) if len(vaudio) else None
    red.rpush('w-audio',  *audio)  if len(audio)  else None

if Term.args.purge:
    red.delete('done', 'doing', 'failed')

if len(Term.args.urls):
    Downloads()

if Term.args.sync:
    Scan()
    ResetJobs()
    SyncProbes()
    SyncJobs()

if Term.args.keys:
    workers.start()
