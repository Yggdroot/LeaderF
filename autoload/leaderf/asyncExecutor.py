import sys
import subprocess
import threading
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

    def _readerThread(self, fd, queue, process):
        try:
            for line in iter(fd.readline, b""):
                queue.put(line)
        except:
            process.terminate()
        finally:
            queue.put(None)

    def execute(self, cmd, cleanup=None):
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=False)

        stdout_thread = threading.Thread(target=self._readerThread,
                                         args=(process.stdout, self._outQueue, process))
        stdout_thread.daemon = True
        stdout_thread.start()

        stderr_thread = threading.Thread(target=self._readerThread,
                                         args=(process.stderr, self._errQueue, process))
        stderr_thread.daemon = True
        stderr_thread.start()

        def read(fd, outQueue, errQueue, cleanup):
            try:
                for line in iter(outQueue.get, None):
                    yield line.rstrip(b"\r\n")

                err = b"".join(iter(errQueue.get, None))
                if err:
                    raise Exception(lfEncode(lfBytes2Str(err)))
            finally:
                try:
                    fd.close()
                except IOError:
                    pass

                if cleanup:
                    cleanup()

        stdout_thread.join(0.01)

        out = read(process.stdout, self._outQueue, self._errQueue, cleanup)

        return out


if __name__ == "__main__":
    executor = AsyncExecutor()
    out = executor.execute("ctags -f- -R")
    print("stdout begin: ============================================")
    for i in out:
        print(repr(i))
    print("stdout end: ==============================================")
