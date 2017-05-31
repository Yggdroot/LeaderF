import sys
import subprocess
import threading

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

    def _readerThread(self, fd, queue):
        try:
            for line in iter(fd.readline, b""):
                queue.put(line)
        finally:
            queue.put(None)

    def execute(self, cmd, cleanup=None):
        process = subprocess.Popen(cmd, shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=False)

        stdout_thread = threading.Thread(target=self._readerThread,
                                         args=(process.stdout, self._outQueue))
        stdout_thread.daemon = True
        stdout_thread.start()

        stderr_thread = threading.Thread(target=self._readerThread,
                                         args=(process.stderr, self._errQueue))
        stderr_thread.daemon = True
        stderr_thread.start()

        def read(fd, queue, cleanup):
            try:
                for line in iter(queue.get, None):
                    yield line.rstrip(b"\r\n")
            finally:
                fd.close()
                if cleanup:
                    cleanup()

        stdout_thread.join(0.01)

        out = read(process.stdout, self._outQueue, cleanup)
        err = read(process.stderr, self._errQueue, None)

        return (out, err)


if __name__ == "__main__":
    executor = AsyncExecutor()
    out, err = executor.execute("ctags -f- -R")
    print("stdout begin: ============================================")
    for i in out:
        print(repr(i))
    print("stdout end: ==============================================")
    print("stderr begin: ============================================")
    for i in err:
        print(repr(i))
    print("stderr end: ==============================================")
