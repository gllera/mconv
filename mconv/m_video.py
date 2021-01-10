from shutil import move
from .libs import args, tempfile, call, do_group

ext = '.mp4'

def needs_change(file):
   ac = file['ac'] and ( file['ac'][0] != 'aac'  or file['ac'][1] > 128100 )
   vc = file['vc'] and ( file['vc'][0] != 'h264' or file['vc'][1] > 600000 )

   return ac, vc



def test(file):
   if file['suffix'] != ext or not ( do_group(2) or do_group(3) ):
      return False

   bad_ac, bad_vc = needs_change(file)

   if do_group(2):
      if do_group(3):
         return bad_ac or bad_vc
      return bad_ac and not bad_vc
   return bad_vc



def process(file):
   if not test(file):
      return False

   output = tempfile()
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
