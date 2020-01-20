import os

VIDEO_EXTS = ['.' + x.lower() for x in os.environ['VIDEO_EXTS'].split(',')]
AUDIO_EXTS = ['.' + x.lower() for x in os.environ['AUDIO_EXTS'].split(',')]

REDIS_HOST = os.environ['REDIS_HOST']
LIBRARY = os.environ['LIBRARY']
TEMPORAL = os.environ['TEMPORAL']

ALL_EXTS = VIDEO_EXTS + AUDIO_EXTS
