import sys
from queue import Queue
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog
import logging
from Logger.log_streamer import setup_logging, LogStreamer, LogReceiver
from controllers.commander import Enumerations
from ui.epra import EpraController, EPRA
from ui.etsra import ETSRA, EtsraController
from ui.user_validator import user_authorized
from ui.report_type_generator import ReportGenerator

logger = logging.getLogger('main')

queue = Queue()


if __name__ == '__main__':
    if user_authorized():
        log_stream = LogStreamer(queue)
        sys.stderr = log_stream
        setup_logging(log_stream)
        qapp = QApplication(sys.argv)
        font = qapp.font()
        font.setFamily("Calibri Light")
        font.setPointSize(10)
        qapp.setFont(font)
        qapp.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        session_loader = ReportGenerator()
        if session_loader.exec_() == QDialog.Accepted:
            if session_loader.program_decider == Enumerations.ProgramDecider.EPRA:
                controller = EpraController()
                Gui = EPRA(controller)
                log_receiver = LogReceiver(log_stream)
                log_receiver.log_signal.connect(Gui.append_text)
                log_receiver.start()
                qapp.exec_()

            elif session_loader.program_decider == Enumerations.ProgramDecider.ETSRA:
                controller = EtsraController()
                Gui = ETSRA(controller)
                log_receiver = LogReceiver(log_stream)
                log_receiver.log_signal.connect(Gui.append_text)
                log_receiver.start()
                qapp.exec_()

            else:
                msg_box = QtWidgets.QMessageBox()
                msg_box.setIcon(QtWidgets.QMessageBox.Warning)
                msg_box.setWindowTitle("Warning")
                msg_box.setText("Unknown program decider selected.")
                msg_box.exec_()



