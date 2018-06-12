import os
import sys
import shlex
import signal
import threading
import subprocess
from .utils import *

if sys.version_info >= (3, 0):
    import queue as Queue
else:
    import Queue


class AsyncExecutor(object):
    """
    A class to implement executing a command in subprocess, then
    read the output asynchronously.
    """
    def __init__(self):
        self._outQueue = Queue.Queue()
        self._errQueue = Queue.Queue()
        self._process = None
        self._finished = False

    def _readerThread(self, fd, queue, is_out):
        try:
            for line in iter(fd.readline, b""):
                queue.put(line)
        except ValueError:
            pass
        finally:
            queue.put(None)
            if is_out:
                self._finished = True

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

        self._finished = False

        stdout_thread = threading.Thread(target=self._readerThread,
                                         args=(self._process.stdout, self._outQueue, True))
        stdout_thread.daemon = True
        stdout_thread.start()

        stderr_thread = threading.Thread(target=self._readerThread,
                                         args=(self._process.stderr, self._errQueue, False))
        stderr_thread.daemon = True
        stderr_thread.start()

        def read(outQueue, errQueue, encoding, cleanup):
            try:
                if encoding:
                    while True:
                        try:
                            line = outQueue.get(True, 0.01)
                            if line is None:
                                break
                            yield lfBytes2Str(line.rstrip(b"\r\n"), encoding)
                        except Queue.Empty:
                            yield None
                else:
                    while True:
                        try:
                            line = outQueue.get(True, 0.01)
                            if line is None:
                                break
                            yield lfEncode(lfBytes2Str(line.rstrip(b"\r\n")))
                        except Queue.Empty:
                            yield None

                err = b"".join(iter(errQueue.get, None))
                if err:
                    raise Exception(lfBytes2Str(err, encoding))
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
        # Popen.poll always returns None, bug?
        # if self._process and not self._process.poll():
        if self._process and not self._finished:
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
