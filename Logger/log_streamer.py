import logging
import threading

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

DEFAULT_LEVEL = logging.DEBUG


def setup_logging(log_stream):
    std_out_handler = logging.StreamHandler(log_stream)
    formatter = logging.Formatter('%(asctime)s-%(name)10s- %(process)s -%(levelname)8s: %(message)s', "%a %d %H:%M:%S")
    std_out_handler.setFormatter(formatter)
    logging.getLogger().addHandler(std_out_handler)
    logging.getLogger().setLevel(DEFAULT_LEVEL)


class LogStreamer:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def read(self):
        return self.queue.get()

    def flush(self):
        pass

class LogReceiver(QObject, threading.Thread):
    log_signal = pyqtSignal(object)

    def __init__(self, log_streamer, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        threading.Thread.__init__(self)
        super(LogReceiver, self).__init__()
        self._log_streamer = log_streamer
        self.daemon = True

    @pyqtSlot()
    def run(self):
        while True:
            text = self._log_streamer.read()
            self.log_signal.emit(text)



def log_parser(line):
    if "INFO" in line:
        return "<span style='color: Green'>{}".format(line)
    elif "ERROR" in line:
        return "<span style='color: Red'>{}".format(line)
    elif "DEBUG" in line:
        return "<span style='color: Blue'>{}".format(line)
    else:
        return "<span style='color: Black'>{}".format(line)
