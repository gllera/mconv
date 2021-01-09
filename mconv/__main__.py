#!/usr/bin/env python

from csv import reader, writer
from os import walk
from pathlib import Path
from traceback import format_exc

from .     import m_audio, m_video, m_probe
from .libs import args, db, tmp, file_to_storeRow, storedRow_to_file, job_queue, start_workers, stop_workers

tmp.mkdir(exist_ok=True)


def processor(file):
   try:
      if not file['mt']:
         file['mt'] = int( file['path'].stat().st_mtime )

      if not file['pt'] or file['pt'] != file['mt']:
         m_probe.process(file)

      if ( m_audio.process(file) or m_video.process(file) ) and args.sync:
         file['mt'] = int( file['path'].stat().st_mtime )
         m_probe.process(file)

   except Exception:
      file['pt'] = file['ac'] = file['vc'] = None
      raise



def gen_files():
   db_reader = reader(open(db, encoding='utf-8'), delimiter='|') if db.exists() else None

   if args.sync:
      stored = { row[0] : row for row in db_reader } if db_reader else {}

      for dirpath, dirs, files in walk('.'):
         dirs[:] = [d for d in dirs if not d.startswith('.')]

         for i in files:
            path = Path(dirpath, i)
            yield storedRow_to_file( path, stored.get(path.as_posix()) )
   else:
      for row in db_reader if db_reader else []:
         yield storedRow_to_file( Path(row[0]), row )



to_store = []
start_workers(processor)

for file in gen_files():
   if file['suffix'] not in m_probe.exts:
      continue

   if args.sync:
      to_store.append(file)

      file['mt'] = int( file['path'].stat().st_mtime )

      if not file['pt'] or file['pt'] != file['mt']:
         job_queue.put(file)
         continue

   if m_audio.test(file) or m_video.test(file):
      job_queue.put(file)

stop_workers()



if args.sync:
   fo_raw = open( db, 'w', encoding='utf-8', newline='' )
   fo = writer( fo_raw, delimiter='|', lineterminator='\n' )

   for v in to_store:
      if v['pt']:
         fo.writerow( file_to_storeRow(v) )

print()
print('All done!!')
