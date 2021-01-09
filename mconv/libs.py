from subprocess import run, PIPE, STDOUT
from shlex import join
from pathlib import Path
from random import choices
from string import ascii_letters, digits
from argparse import ArgumentParser
from os import cpu_count, chdir
from platform import system
from sys import stderr, exit
from queue import Queue
from threading import Thread
from signal import signal, SIGINT
from time import sleep


_parser = ArgumentParser( prog='mconv', description='Multimedia library maintainer' )
_parser.add_argument ( '-l', '--load',                               help='Process tasks with CPU load: 1 (Low) - 3 (High)',   type=int )
_parser.add_argument ( '-j', '--jobs',                               help='Number of paralell jobs',   type=int )
_parser.add_argument ( '-s', '--sync',   action='store_true',        help='Sync database file (default on "load=1" or "load undefined")' )
_parser.add_argument ( '-n', '--nvidia', action='store_true',        help='Use nvidia hardware when necessary' )
_parser.add_argument ( '-f', '--fix',    action='store_true',        help='Attempt to fix the video first before convert it' )
_parser.add_argument ( 'path', nargs=1,                              help='Path where multimedia library is',  type=lambda x: Path(x) )

args = _parser.parse_args()
chdir( args.path[0] )
db = Path('.db')
tmp = Path('.tmp')

if not args.sync:
   args.sync = not args.load or args.load == 1

if not args.jobs:
   args.jobs = 1

   if args.load:
      if args.load == 1:
         args.jobs = cpu_count() * 2
      elif args.load == 2:
         args.jobs = cpu_count()


global running
running = True

job_queue = Queue()
workers = []

def worker_loop(processor):
   global running

   while running:
      try:
         file = job_queue.get()
         if file:
            processor(file)
         else:
            break
      except Exception as e:
         if running:
            if len(e.args) == 2:
               print(' E ', e.args[0], e.args[1])
            else:
               print(' E ', str(e))

def start_workers(processor):
   for i in range(args.jobs):
      worker = Thread( target=worker_loop, args=(processor,) )
      workers.append( worker )
      worker.start()

def stop_workers(forced=False):
   if not forced:
      while not job_queue.empty():
         sleep(0.1)

   global running
   running = False

   for i in range(args.jobs):
      job_queue.put(None)

   for worker in workers:
      worker.join()

def _kill(signum, frame):
   stop_workers(True)
   exit(0)

signal( SIGINT,  _kill )


def call(cmd):
   res = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, encoding='utf-8')

   if res.returncode:
      raise Exception('CMD failed:', join(cmd))

   return res.stdout



def tempfile():
   res = None

   while True:
      res = Path( tmp, ''.join(choices(ascii_letters + digits, k=16)))
      if not res.exists():
         break

   return res



def storedRow_to_file(path, row):
   res = {
       'path': path,
       'suffix': path.suffix.lower(),
       'mt': None,
       'pt': None,
       'ac': None,
       'vc': None,
   }

   if row and row[1]:
      res['pt'] = int(row[1])

      if row[2]:
         res['ac'] = ( row[2], int(row[3]) )
      if row[4]:
         res['vc'] = ( row[4], int(row[5]) )

   return res


def file_to_storeRow(file):
   return [
      file['path'].as_posix(),
      file['pt'],
      file['ac'][0] if file['ac'] else None,
      file['ac'][1] if file['ac'] else None,
      file['vc'][0] if file['vc'] else None,
      file['vc'][1] if file['vc'] else None,
   ]
