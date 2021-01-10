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
from shutil import which

try:
   from .version import __version__
except ModuleNotFoundError:
   __version__='0.0.0-local'


_parser = ArgumentParser( prog='mconv', description='Multimedia library converter v' + __version__ )
_parser.add_argument ( '-t', '--tier',   action='append',     help='Subgroups of tasks to process based on CPU demand: 1 (Low) - 3 (High)', dest="M",  type=int )
_parser.add_argument ( '-j', '--jobs',                        help='Number of paralell jobs',   type=int, dest="N" )
_parser.add_argument ( '-n', '--nvidia', action='store_true', help='Use nvidia hardware when necessary' )
_parser.add_argument ( 'path', nargs=1,                       help='Library path',  type=lambda x: Path(x) )

args = _parser.parse_args()
chdir( args.path[0] )
db = Path('.db')
tmp = Path('.tmp')
groups_bin = 31

for i in [ 'ffmpeg', 'ffprobe' ]:
   if not which(i):
      print( 'Error, not found on PATH:', i )
      exit(0)

if args.M:
   groups_bin = 0

   for rest in args.M:
      while rest > 0:
         i = int(rest % 10)
         rest = int(rest / 10)
         if i < 4:
            groups_bin = groups_bin | 1 << i

def do_group(id):
   return groups_bin & 1 << id

if not args.N:
   if do_group(3):
      args.N = 1
   elif do_group(2):
      args.N = cpu_count()
   else:
      args.N = cpu_count() * 2


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
   for i in range(args.N):
      worker = Thread( target=worker_loop, args=(processor,) )
      workers.append( worker )
      worker.start()

def stop_workers(forced=False):
   if not forced:
      while not job_queue.empty():
         sleep(0.1)

   global running
   running = False

   for i in range(args.N):
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
