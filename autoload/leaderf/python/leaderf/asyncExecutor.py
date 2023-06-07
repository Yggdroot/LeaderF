import os
import sys
import shlex
import signal
import threading
import itertools
import subprocess
from .utils import *

if sys.version_info >= (3, 0):
    import queue as Queue
    lfDEVNULL = subprocess.DEVNULL
else:
    import Queue
    lfDEVNULL = open(os.devnull)


class AsyncExecutor(object):
    """
    A class to implement executing a command in subprocess, then
    read the output asynchronously.
    """
    def __init__(self):
        self._errQueue = Queue.Queue()
        self._process = None
        self._finished = False
        self._max_count = int(lfEval("g:Lf_MaxCount"))

    def _readerThread(self, fd, queue):
        try:
            for line in iter(fd.readline, b""):
                queue.put(line)
        except ValueError:
            pass
        finally:
            queue.put(None)

    def execute(self, cmd, encoding=None, cleanup=None, env=None, raise_except=True, format_line=None):
        if os.name == 'nt':
            self._process = subprocess.Popen(cmd, bufsize=-1,
                                             stdin=lfDEVNULL,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             shell=True,
                                             env=env,
                                             universal_newlines=False)
        else:
            self._process = subprocess.Popen(cmd, bufsize=-1,
                                             stdin=lfDEVNULL,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             preexec_fn=os.setsid,
                                             shell=True,
                                             env=env,
                                             universal_newlines=False)

        self._finished = False

        stderr_thread = threading.Thread(target=self._readerThread,
                                         args=(self._process.stderr, self._errQueue))
        stderr_thread.daemon = True
        stderr_thread.start()

        if sys.version_info >= (3, 0):
            def read(source):
                try:
                    count = 0
                    if encoding:
                        for line in source:
                            try:
                                line.decode("ascii")
                                yield (
                                    format_line(line.rstrip(b"\r\n").decode())
                                ) if format_line else line.rstrip(b"\r\n").decode()
                            except UnicodeDecodeError:
                                yield (
                                    format_line(lfBytes2Str(line.rstrip(b"\r\n"), encoding))
                                ) if format_line else (
                                    lfBytes2Str(line.rstrip(b"\r\n"), encoding)
                                )
                            if self._max_count > 0:
                                count += 1
                                if count >= self._max_count:
                                    self.killProcess()
                                    break
                    else:
                        for line in source:
                            try:
                                line.decode("ascii")
                                yield (
                                    format_line(line.rstrip(b"\r\n").decode())
                                ) if format_line else line.rstrip(b"\r\n").decode()
                            except UnicodeDecodeError:
                                yield (
                                    format_line(lfBytes2Str(line.rstrip(b"\r\n")))
                                ) if format_line else lfBytes2Str(line.rstrip(b"\r\n"))
                            if self._max_count > 0:
                                count += 1
                                if count >= self._max_count:
                                    self.killProcess()
                                    break

                    err = b"".join(iter(self._errQueue.get, None))
                    if err and raise_except:
                        raise Exception(lfBytes2Str(err) + lfBytes2Str(err, encoding))
                except ValueError:
                    pass
                finally:
                    self._finished = True
                    try:
                        if self._process:
                            self._process.stdout.close()
                            self._process.stderr.close()
                            self._process.poll()
                    except IOError:
                        pass

                    if cleanup:
                        cleanup()
        else:
            def read(source):
                try:
                    count = 0
                    if encoding:
                        for line in source:
                            yield (
                                format_line(line.rstrip(b"\r\n"))
                            ) if format_line else line.rstrip(b"\r\n")
                            if self._max_count > 0:
                                count += 1
                                if count >= self._max_count:
                                    self.killProcess()
                                    break
                    else:
                        for line in source:
                            try:
                                line.decode("ascii")
                                yield (
                                    format_line(line.rstrip(b"\r\n"))
                                ) if format_line else line.rstrip(b"\r\n")
                            except UnicodeDecodeError:
                                yield (
                                    format_line(lfEncode(line.rstrip(b"\r\n")))
                                ) if format_line else lfEncode(line.rstrip(b"\r\n"))
                            if self._max_count > 0:
                                count += 1
                                if count >= self._max_count:
                                    self.killProcess()
                                    break

                    err = b"".join(iter(self._errQueue.get, None))
                    if err and raise_except:
                        raise Exception(lfEncode(err) + err)
                except ValueError:
                    pass
                finally:
                    self._finished = True
                    try:
                        if self._process:
                            self._process.stdout.close()
                            self._process.stderr.close()
                            self._process.poll()
                    except IOError:
                        pass

                    if cleanup:
                        cleanup()

        result = AsyncExecutor.Result(read(iter(self._process.stdout.readline, b"")))

        return result

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

    class Result(object):
        def __init__(self, iterable):
            self._g = iterable

        def __add__(self, iterable):
            self._g = itertools.chain(self._g, iterable)
            return self

        def __iadd__(self, iterable):
            self._g = itertools.chain(self._g, iterable)
            return self

        def join_left(self, iterable):
            self._g = itertools.chain(iterable, self._g)
            return self

        def __iter__(self):
            return self._g


if __name__ == "__main__":
    executor = AsyncExecutor()
    out = executor.execute("ctags -f- -R")
    print("stdout begin: ============================================")
    for i in out:
        print(repr(i))
    print("stdout end: ==============================================")
