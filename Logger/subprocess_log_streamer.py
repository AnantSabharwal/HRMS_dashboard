import logging
import sys
import threading
import traceback

from Logger.log_streamer import DEFAULT_LEVEL


class SubProcessLogHandler(logging.Handler):
    """handler used by subprocesses

    It simply puts items on a Queue for the main process to log.

    """

    def __init__(self, queue):
        logging.Handler.__init__(self)
        self.queue = queue

    def emit(self, record):
        self.queue.put(record)


class LogQueueReader(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True

    def run(self):
        while True:
            try:
                record = self.queue.get()
                # get the logger for this record
                logger = logging.getLogger(record.name)
                logger.callHandlers(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)


def setup_logger(name, log_queue):
    logger = logging.getLogger(name)
    for handler in logger.handlers:
        assert not isinstance(handler, SubProcessLogHandler)
        logger.removeHandler(handler)
    handler = SubProcessLogHandler(log_queue)
    logger.addHandler(handler)
    logger.setLevel(DEFAULT_LEVEL)
    return logger

