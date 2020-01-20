import threading
import re
import os
import uuid
import shutil
import json

class Workers:
    def __init__(self, conf, term, executor, redis):
        self.keys = term.args.keys
        self.term = term
        self.redis = redis
        self.done_path = os.path.join( conf.TEMPORAL, 'done' )
        self.work_path = os.path.join( conf.TEMPORAL, 'ongoing' )
        self.library_path = conf.LIBRARY
        self.exe = executor()
        
        self.threads = []
        self.running = False

        os.makedirs(self.done_path, exist_ok = True)
        os.makedirs(self.work_path, exist_ok = True)

        for i in range(term.args.jobs):
            self.threads.append( threading.Thread( target=self._loop ))

    def start(self):
        self.running = True

        for i in self.threads:
            i.start()

    def _saveRes(self, txt, res):
        with self.redis.pipeline() as pipe:
            if res:
                self.redis.hset('done', txt, 1)
                self.redis.hdel('failed', txt)
            else:
                self.redis.hset('failed', txt, 1)

            self.redis.hdel('doing', txt)

    def _parsePop(self, pop):
        if not pop:
            return None, None, None, None

        jobId, order = pop
        tmp = order.split('|')
        job = tmp[-1]
        dest = tmp[0]

        if jobId == 'w-download':
            dest = os.path.join(self.done_path, dest)
        elif jobId == 'w-torrent':
            dest = self.done_path
        else:
            job = os.path.join(self.library_path, job)
            dest = os.path.join(self.done_path, job)

        return jobId, job, dest, '%s|%s' % (jobId, order)

    def _parseProbeOutput(self, output):
        js = json.loads(''.join(output))

        if 'streams' in js:
            for i in js['streams']:
                if 'codec_type' in i and 'codec_name' in i:
                    ctype = i['codec_type']
                    cname = i['codec_name']

        print(  )

    def _run(self, jobId, tmp, job):
        if jobId == 'w-probe':
            return self.exe.run(jobId, job)
        else:
            return self.exe.run(jobId, tmp, job)

    def _loop(self):
        tmp = os.path.join(self.work_path, str(uuid.uuid4()))

        while self.running:
            jobId, job, dest, txt = self._parsePop( self.redis.blpop(self.keys, 1) )

            if jobId and not self.redis.hexists('done', txt) and self.redis.hset('doing', txt, 1) == 1:
                shutil.rmtree(tmp, ignore_errors=True)
                
                if jobId == 'w-torrent':
                    os.makedirs(tmp)

                res, output = self._run(jobId, tmp, job)

                if res:
                    if jobId == 'w-torrent':
                        for f in os.listdir(tmp):
                            os.rename( os.path.join(tmp, f), os.path.join(dest, f))
                    elif jobId == 'w-probe':
                        self._parseProbeOutput(output)
                    else:
                        os.makedirs(os.path.dirname(dest), exist_ok = True)
                        os.rename(tmp, dest)

                self._saveRes(txt, res)
