import os
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot

from controllers.commander import CommanderEPRA, CommanderETSRA, Enumerations
from ui.epra import EPRA
from ui.etsra import ETSRA


# class ReportController:
#     def __init__(self):
#         self.something = None
#
#     def timesheet_report(self):
#         pass
#
#     def employee_performance_report(self):
#         pass
#

class ReportGenerator(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        # self._controller = controller
        self._icon_path = os.path.join(str(Path(__file__).parents[1]), "ui", "icons")
        self._program_to_run = None
        self._report_type = None
        self.setLayout(self._create_layout())
        self.setWindowTitle("Multipurpose Report Generator")
        self.setWhatsThis("This gives the user the opportunity to generate number of reports using a click of the "
                          "button. This helps save time for generating reports.")
        self.setMinimumSize(400,150)
        self.setWindowIcon(QIcon("ui/icons/Logo.png"))

    @property
    def program_decider(self):
        return self._program_to_run

    @program_decider.setter
    def program_decider(self, prog):
        self._program_to_run = prog

    def _create_layout(self):
        layout = QVBoxLayout()
        self._timesheet_report_btn = QPushButton("TimeSheet Report Generator")
        self._timesheet_report_btn.clicked.connect(self._start_timesheet_report_generation_session)
        self._epr_btn = QPushButton("Employee Performance Report Generator")
        self._epr_btn.clicked.connect(self._start_epr_generation_session)
        layout.addWidget(self._timesheet_report_btn)
        layout.addWidget(self._epr_btn)
        return layout

    @pyqtSlot()
    def _start_timesheet_report_generation_session(self):
        # timesheet_dialog = TimesheetReportDialog()

        # self.program_decider(Enumerations.program_decider.ETSRA.value)
        self.program_decider = Enumerations.ProgramDecider.ETSRA
        self.accept()
        print("Timesheet report generator worked")

    @pyqtSlot()
    def _start_epr_generation_session(self):
        self.program_decider = Enumerations.ProgramDecider.EPRA
        self.accept()
        print("EPRA report generator worked")
