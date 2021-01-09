from libs import args, tempfile, call
from shutil import move

ext = '.mp4'

def needs_change(file):
   ac = file['ac'] and ( file['ac'][0] != 'aac'  or file['ac'][1] > 128100 )
   vc = file['vc'] and ( file['vc'][0] != 'h264' or file['vc'][1] > 600000 )

   if ( args.load == 2 and vc ) or ( args.load == 3 and not vc ):
      return False, False

   return ac, vc



def test(file):
   if args.load == 1 or file['suffix'] != ext:
      return False

   return any( needs_change(file) )



def process(file):
   if not test(file):
      return False

   output = tempfile()

   if args.fix:
      print( ' R ', file['path'] )
      call( [ 'ffmpeg', '-hide_banner', '-y', '-i', str(file['path']), '-c', 'copy', '-f', 'avi', str(output) ] )
      move( output, file['path'] )

   bad_ac, bad_vc = needs_change(file)

   cmd  = [ 'ffmpeg', '-hide_banner', '-y' ]
   cmd += [ '-hwaccel', 'nvdec' ]               if args.nvidia else []
   cmd += [ '-i', str(file['path']), '-c:a' ]
   cmd += [ 'copy' ]                            if not bad_ac  else [ 'aac',  '-b:a', '100k' ]
   cmd += [ '-c:v' ]
   cmd += [ 'copy' ]                            if not bad_vc  else [ 'h264_nvenc' ] if args.nvidia else [ 'h264' ]
   cmd += [ '-vsync', '2', '-r', '30', '-vf', 'scale=1280x1280:force_original_aspect_ratio=decrease', '-b:v', '500k', '-movflags', '+faststart' ] if bad_vc else []
   cmd += [ '-f', 'mp4', str(output) ]

   print( ' > ', file['path'] )
   call( cmd )
   move( output, file['path'] )

   return True
