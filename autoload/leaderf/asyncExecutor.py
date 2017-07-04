import os
import sys
import shlex
import signal
import threading
import subprocess
from leaderf.utils import *

if sys.version_info >= (3, 0):
    from queue import Queue
else:
    from Queue import Queue


class AsyncExecutor(object):
    """
    A class to implement executing a command in subprocess, then
    read the output asynchronously.
    """
    def __init__(self):
        self._outQueue = Queue()
        self._errQueue = Queue()
        self._process = None

    def _readerThread(self, fd, queue):
        try:
            for line in iter(fd.readline, b""):
                queue.put(line)
        finally:
            queue.put(None)

    def execute(self, cmd, encoding=None, cleanup=None):
        if os.name == 'nt':
            self._process = subprocess.Popen(cmd, bufsize=-1,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             shell=True,
                                             universal_newlines=False)
        else:
            self._process = subprocess.Popen(cmd, bufsize=-1,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             preexec_fn=os.setsid,
                                             shell=True,
                                             universal_newlines=False)

        stdout_thread = threading.Thread(target=self._readerThread,
                                         args=(self._process.stdout, self._outQueue))
        stdout_thread.daemon = True
        stdout_thread.start()

        stderr_thread = threading.Thread(target=self._readerThread,
                                         args=(self._process.stderr, self._errQueue))
        stderr_thread.daemon = True
        stderr_thread.start()

        def read(outQueue, errQueue, encoding, cleanup):
            try:
                if encoding:
                    for line in iter(outQueue.get, None):
                        yield lfBytes2Str(line.rstrip(b"\r\n"), encoding)
                else:
                    for line in iter(outQueue.get, None):
                        yield lfEncode(lfBytes2Str((line.rstrip(b"\r\n"))))

                err = b"".join(iter(errQueue.get, None))
                if err:
                    raise Exception(lfEncode(lfBytes2Str(err)))
            finally:
                try:
                    if self._process:
                        self._process.stdout.close()
                except IOError:
                    pass

                if cleanup:
                    cleanup()

        stdout_thread.join(0.01)

        out = read(self._outQueue, self._errQueue, encoding, cleanup)

        return out

    def killProcess(self):
        if self._process and not self._process.poll():
            if os.name == 'nt':
                subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self._process.pid), shell=True)
            else:
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                except OSError:
                    pass

            self._process = None


if __name__ == "__main__":
    executor = AsyncExecutor()
    out = executor.execute("ctags -f- -R")
    print("stdout begin: ============================================")
    for i in out:
        print(repr(i))
    print("stdout end: ==============================================")
