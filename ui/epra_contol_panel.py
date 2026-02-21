import logging
import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QButtonGroup, QRadioButton, QPushButton, QVBoxLayout, \
    QLabel, QToolBar
from controllers.commander import Enumerations, CommanderEPRA


class EPRAControlPanel(QWidget):
    def __init__(self):
        # type: () -> None
        QWidget.__init__(self)
        self._commander = CommanderEPRA()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._icons = os.path.join(str(Path(__file__).parents[1]), "ui", "icons")

    def designation_ver_selection(self):
        selection_widget = QGroupBox("Employee Designations.")
        selection_layout = QHBoxLayout()
        rd_group = QButtonGroup()
        self.admin_radio = QRadioButton("Admin")
        self.AE_radio = QRadioButton("AE")
        self.HR_radio = QRadioButton("HR")
        self.PE_radio = QRadioButton("PE")
        self.SE_radio = QRadioButton("SE")
        self.admin_radio.toggled.connect(self._select_designation)
        rd_group.addButton(self.admin_radio)
        rd_group.addButton(self.AE_radio)
        rd_group.addButton(self.HR_radio)
        rd_group.addButton(self.PE_radio)
        rd_group.addButton(self.SE_radio)
        selection_layout.addWidget(self.admin_radio)
        selection_layout.addWidget(self.AE_radio)
        selection_layout.addWidget(self.HR_radio)
        selection_layout.addWidget(self.PE_radio)
        selection_layout.addWidget(self.SE_radio)
        selection_widget.setLayout(selection_layout)
        return selection_widget

    def _select_designation(self):
        if self.admin_radio.isChecked():
            self._commander.employee_designation = Enumerations.DesignationVer.ADMIN.value
        elif self.HR_radio.isChecked():
            self._commander.employee_designation = Enumerations.DesignationVer.HR.value
        elif self.AE_radio.isChecked():
            self._commander.employee_designation = Enumerations.DesignationVer.AE.value
        elif self.PE_radio.isChecked():
            self._commander.employee_designation = Enumerations.DesignationVer.PE.value
        elif self.SE_radio.isChecked():
            self._commander.employee_designation = Enumerations.DesignationVer.SE.value

    def excel_name_bar(self):
        xl_gb = QGroupBox("Loaded Excel")
        xl_lay = QHBoxLayout()
        self._label_xl = QLabel("Case: ")
        xl_lay.addWidget(self._label_xl, Qt.AlignCenter)
        xl_gb.setLayout(xl_lay)
        return xl_gb

    def update_excel_label(self,path):
        path = str(path)
        basename, ext = os.path.splitext(path)
        if (ext == '.xlsx') or (ext == '.xls'):
            self._label_xl.setText(
                "<span style='color:blue; font-weight: 1000'>Excel: " + str(os.path.basename(path)))
        else:
            self._label_xl.setText(
                "<span style='color:red; font-weight: 1000'>" + str(path))

    def upload_excel(self):
        excel_gb = QGroupBox("Excel Uploader")
        excel_lay = QVBoxLayout()
        self.btn_upload_excel = QPushButton("Upload\nExcel")
        excel_lay.addWidget(self.btn_upload_excel)
        excel_gb.setLayout(excel_lay)
        return excel_gb

    def generate_results(self):
        result_gb = QGroupBox("Generate Results")
        result_layout = QHBoxLayout()
        self.btn_open_generation_selection = QPushButton("Generate\nResults\nSave as Excel")
        self.btn_open_generation_selection.setToolTip("Clicking this preprocesses the selected file and generates "
                                                      "final output files as excel.")
        self.btn_open_generation_selection.setIcon(QIcon(os.path.join(self._icons, "Run.png")))
        result_layout.addWidget(self.btn_open_generation_selection)
        result_gb.setLayout(result_layout)
        return result_gb

    def download_results_pdf(self):
        result_gb = QGroupBox("Save Results PDF")
        result_layout = QHBoxLayout()
        self.btn_open_download_pdf_selection = QPushButton("Save\nto\nPDF")
        self.btn_open_download_pdf_selection.setToolTip(
            "Downloads the results in the form of a pdf.")
        self.btn_open_download_pdf_selection.setIcon(QIcon(os.path.join(self._icons, "pdf.png")))
        result_layout.addWidget(self.btn_open_download_pdf_selection)
        result_gb.setLayout(result_layout)
        return result_gb

