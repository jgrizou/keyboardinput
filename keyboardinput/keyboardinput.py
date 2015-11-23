
# some reference
# http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
# https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/

import os
import sys
import termios
import fcntl

import Queue
import threading


DEFAULT_INTERRUPT_CODE = 3  # CTRL-C on linux, ord(read value form stdin)


class KeyboardInput(threading.Thread):

    def __init__(self, interrupt_code=DEFAULT_INTERRUPT_CODE):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interrupted = threading.Lock()

        self.interrupt_code = interrupt_code
        self.queue = Queue.Queue()

    def stop(self):
        self.interrupted.release()

    def run(self):
        self.interrupted.acquire()
        while not self.interrupted.acquire(False):
            ret = self.read_single_keypress()
            if ord(ret) == self.interrupt_code:
                self.stop()
            else:
                self.queue.put(ret)

    # from http://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
    def read_single_keypress(self):
        """Waits for a single keypress on stdin.

        This is a silly function to call if you need to do it a lot because it has
        to store stdin's current setup, setup stdin for reading single keystrokes
        then read the single keystroke then revert stdin back after reading the
        keystroke.

        Returns the character of the key that was pressed (zero on
        KeyboardInterrupt which can happen when a signal gets handled)

        """

        fd = sys.stdin.fileno()
        # save old state
        flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
        attrs_save = termios.tcgetattr(fd)
        # make raw - the way to do this comes from the termios(3) man page.
        attrs = list(attrs_save)  # copy the stored version to update
        # iflag
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                      | termios.ISTRIP | termios.INLCR | termios. IGNCR
                      | termios.ICRNL | termios.IXON)
        # oflag
        attrs[1] &= ~termios.OPOST
        # cflag
        attrs[2] &= ~(termios.CSIZE | termios. PARENB)
        attrs[2] |= termios.CS8
        # lflag
        attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                      | termios.ISIG | termios.IEXTEN)
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        # turn off non-blocking
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
        # read a single keystroke
        try:
            ret = sys.stdin.read(1)  # returns a single character
        finally:
            # restore old state
            termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
        return ret

    def read(self, timeout=None):
        try:
            return self.queue.get(block=True, timeout=timeout)
        except Queue.Empty:
            return None

    def data_available(self):
        return not self.queue.empty()
