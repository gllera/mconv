#!/usr/bin/env python

from csv import reader, writer
from os import walk
from pathlib import Path
from traceback import format_exc

from . import m_audio, m_video, m_probe, libs

libs.tmp.mkdir(exist_ok=True)
stored = {}
to_store = []


def processor(file):
   m_probe.process(file, True)

   if ( m_audio.process(file) or m_video.process(file) ):
      file['mt'] = None
      m_probe.process(file)

def put(path, row):
   file = libs.storedRow_to_file( path, row )

   if file['suffix'] not in m_probe.exts:
      return

   if libs.do_group(1):
      to_store.append(file)

   if m_probe.test(file) or m_audio.test(file) or m_video.test(file):
      libs.job_queue.put(file)



if libs.db.exists():
   fi_raw = open( libs.db, encoding='utf-8' )
   fi = reader( fi_raw, delimiter='|' )
   stored = { row[0] : row for row in fi }

libs.start_workers(processor)

if not libs.do_group(1):
   for k, v in stored.items():
      put( Path( k ), v )
else:
   for dirpath, dirs, files in walk('.'):
      dirs[:] = [d for d in dirs if not d.startswith('.')]

      for i in files:
         path = Path(dirpath, i)
         put( path, stored.get( path.as_posix() ))

libs.stop_workers()

if libs.do_group(1):
   fo_raw = open( libs.db, 'w', encoding='utf-8', newline='' )
   fo = writer( fo_raw, delimiter='|', lineterminator='\n' )

   for v in to_store:
      if v['pt']:
         fo.writerow( libs.file_to_storeRow(v) )

print()
print('All done!!')
