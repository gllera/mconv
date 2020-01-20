import subprocess
import tempfile
import os
import re
import itertools

class Parser():
    def __init__(self, cmd):
        self.cmd = re.sub(' +', ' ', cmd).split(' ')
        self.params = []

        for i in range(len(self.cmd)):
            if self.cmd[i] == '{}':
                self.params.append(i)

    def parse(self, params):
        if len(self.params) != len(params):
            print('Invalid number of params')
            exit(1)

        res = self.cmd.copy()

        for i in range(len(params)):
            res[self.params[i]] = params[i]
        
        return res

class Executor:
    def __init__(self):
        self.fo = open( os.path.join( tempfile.gettempdir(), 'converter.out' ), 'a+' )
        self.counter = itertools.count()

        aria   = 'aria2c --disable-ipv6=true --follow-torrent=mem --seed-time=0 --enable-color=false --check-certificate=false --console-log-level=error --summary-interval=0'
        probe  = 'ffprobe -v quiet -print_format json -show_streams'
        ffmpeg = 'ffmpeg -hide_banner -y'
        ffmpeg_vo = '-vsync 2 -r 30 -vf scale=1280x1280:force_original_aspect_ratio=decrease -b:v 500k -movflags +faststart'
        
        self.cmds = {
            'w-probe'   : Parser('%s {}' % probe),
            'w-download': Parser('%s -d / -o {} {}' % aria),
            'w-torrent' : Parser('%s -d {} {}' % aria),
            'w-hvideo'  : Parser('%s -hwaccel nvdec -i {} -c:a copy           -c:v h264_nvenc %s -f mp4 {}' % ( ffmpeg, ffmpeg_vo )),
            'w-svideo'  : Parser('%s                -i {} -c:a copy           -c:v h264       %s -f mp4 {}' % ( ffmpeg, ffmpeg_vo )),
            'w-vaudio'  : Parser('%s                -i {} -c:a aac  -b:a 100k -c:v copy          -f mp4 {}' % ( ffmpeg )),
            'w-audio'   : Parser('%s                -i {} -c:a mp3  -b:a 128k                    -f mp3 {}' % ( ffmpeg ))
        }

    def run(self, cmdId, *params):
        res = -1
        output = []
        cmd = self.cmds[cmdId].parse([i for i in params])

        jobId = "%04d" % (next(self.counter) % 10000)
        self.fo.write('{}>{}'.format(jobId, ' '.join(cmd)))
    
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
            while True:
                std = process.stdout.readline().decode('utf-8')

                if not std:
                    break
    
                self.fo.write('{} {}'.format(jobId, std))
                output.append(std)
    
            process.wait()
            res = process.returncode
    
        except Exception as e:
            print('Error: %s' % e)
    
        self.fo.write('{}<{}'.format(jobId, res))
        self.fo.flush()

        return res == 0, output

