import threading
import re
import os
import uuid
import subprocess
import tempfile
import shutil
import itertools

parse = redis = conf = term = None
threads = []
running = False

fo = open( os.path.join( tempfile.gettempdir(), 'converter.out' ), 'a+' )
counter = itertools.count()


def init(r, p, t, c):
    global redis, parse, term, conf
    redis, parse, term, conf = r, p, t, c

    for i in range(term.args.jobs):
        threads.append( threading.Thread( target=loop ))


def start():
    global running, threads
    running = True

    for i in threads:
        i.start()


def _exec(jobId, job, tmp):
    output = []
    res = -1
    cmd = parse.cmd(jobId, job, tmp)
    exeId = "%04d" % (next(counter) % 10000)

    print('%s - doing: %s' % (exeId, job))
    fo.write('{}>{}'.format(exeId, ' '.join(cmd)))

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            std = process.stdout.readline().decode('utf-8')

            if not std:
                break

            fo.write('{} {}'.format(exeId, std))
            output.append(std)

        process.wait()
        res = process.returncode

    except Exception as e:
        print('Error: %s' % e)

    print('%s - done.' % exeId)
    fo.write('{}<{}'.format(exeId, res))
    fo.flush()

    return res == 0, output

def loop():
    tmp = os.path.join(conf.WORK_PATH, str(uuid.uuid4()))

    while running:
        jobId, job, dest, txt = parse.redis_pop( redis.blpop(term.args.keys, 1) )
        probe = None

        if jobId and not redis.hexists('done', txt) and redis.hset('doing', txt, 1) == 1:
            shutil.rmtree(tmp, ignore_errors=True)
            
            if jobId == 'w-torrent':
                os.makedirs(tmp)

            res, output = _exec(jobId, job, tmp)

            if res:
                if jobId == 'w-torrent':
                    for f in os.listdir(tmp):
                        os.rename( os.path.join(tmp, f), os.path.join(dest, f) )
                elif jobId == 'w-probe':
                    probe = parse.probe_out(job, output)
                else:
                    os.makedirs(os.path.dirname(dest), exist_ok = True)
                    os.rename(tmp, dest)

            with redis.pipeline(transaction=False) as pipe:
                if res:
                    pipe.hdel('failed', txt)

                    if not probe:
                        pipe.hset('done', txt, 1)
                    else:
                        pipe.hset('probes', probe[0], probe[1])

                        if probe[2]:
                            pipe.rpush(probe[2], probe[0])
                else:
                    pipe.hset('failed', txt, 1)

                pipe.hdel('doing', txt)
                pipe.execute()

