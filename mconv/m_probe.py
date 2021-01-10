from shlex import join
from json import loads

from .     import m_audio, m_video
from .libs import call, do_group

exts = [ m_audio.ext, m_video.ext ]

def test(file, incist=False):
   if not( incist or do_group(1) ):
      return False

   if not file['mt']:
      try:
         file['mt'] = int( file['path'].stat().st_mtime )
      except:
         pass
         file['pt'] = file['ac'] = file['vc'] = None
         print(' E ', 'Not Found:', file['path'])
         return False

   return not file['pt'] or file['pt'] != file['mt']



def process(file, incist=False):
   if not test(file, incist):
      return False

   file['pt'] = file['ac'] = file['vc'] = None

   print( ' ? ', file['path'] )
   stdout = call([ 'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', str(file['path']) ])

   for c in loads(stdout)['streams']:
      type = c.get( 'codec_type', '' )
      name = c.get( 'codec_name', '' )
      rate = c.get( 'bit_rate',   '9999999')

      if type == 'audio':
         file['ac'] = ( name, int(rate) )
      elif type == 'video' and name not in ['mjpeg', 'png']:
         file['vc'] = ( name, int(rate) )

   if not file['ac'] and file['path'].suffix == m_audio.ext:
      raise Exception('BAD Audio:', file['path'])

   if not file['vc'] and file['path'].suffix == m_video.ext:
      raise Exception('BAD Video:', file['path'])

   file['pt'] = file['mt']
