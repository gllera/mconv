import os


REDIS_HOST = '10.0.0.2'
VIDEO_EXTS = 'mp4,m4v,mkv,avi,mov,wmv,wma,flv'
AUDIO_EXTS = 'mp3,wav,aif'

LIBRARY    = '/mnt/data/Courses'
TEMPORAL   = '/mnt/data/converter'

VIDEO_EXTS = ['.' + x.lower() for x in VIDEO_EXTS.split(',')]
AUDIO_EXTS = ['.' + x.lower() for x in AUDIO_EXTS.split(',')]

ALL_EXTS = VIDEO_EXTS + AUDIO_EXTS

DONE_PATH = os.path.join( TEMPORAL, 'done' )
WORK_PATH = os.path.join( TEMPORAL, 'ongoing' )

os.makedirs(DONE_PATH, exist_ok = True)
os.makedirs(WORK_PATH, exist_ok = True)

