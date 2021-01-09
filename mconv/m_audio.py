from shutil import move
from .libs import args, tempfile, call

ext = '.mp3'

def test(file):
   if file['suffix'] != ext:
      return False

   return file['ac'] and ( not args.load or args.load == 2 ) and ( file['ac'][0] != 'mp3' or file['ac'][1] > 128100 )



def process(file):
   if not test(file):
      return False

   output = tempfile()

   print( ' > ', file['path'] )
   call([ 'ffmpeg', '-hide_banner', '-y', '-i', str( file['path'] ), '-c:a', 'mp3', '-b:a', '128k', '-f', 'mp3', str(output) ])
   move( output, file['path'] )

   return True
