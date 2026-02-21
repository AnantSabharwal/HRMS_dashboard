import logging
import os
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QButtonGroup, QRadioButton, QPushButton, QLabel
from controllers.commander import Enumerations


class ETSRAControlPanel(QWidget):
    def __init__(self):
        # type: () -> None
        QWidget.__init__(self)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._icons = os.path.join(str(Path(__file__).parents[1]), "ui", "icons")

    def assign_results_directory(self):
        result_dir_gb = QGroupBox("Assign Excel Directory")
        result_dir_layout = QHBoxLayout()
        self.btn_assign_excel_directory = QPushButton("Select\nExcel\nDirectory")
        self.btn_assign_excel_directory.setToolTip("Assign the directory where the base excel file that has to be analyzed is stored")
        self.btn_assign_excel_directory.setIcon(QIcon(os.path.join(self._icons, "browse.png")))
        result_dir_layout.addWidget(self.btn_assign_excel_directory)
        result_dir_gb.setLayout(result_dir_layout)
        return result_dir_gb

    def generate_results(self):
        result_gb = QGroupBox("Run")
        result_layout = QHBoxLayout()
        self.btn_open_generation_selection = QPushButton("Run")
        self.btn_open_generation_selection.setToolTip("Formats the input data and ")
        self.btn_open_generation_selection.setIcon(QIcon(os.path.join(self._icons, "Run.png")))
        result_layout.addWidget(self.btn_open_generation_selection)
        result_gb.setLayout(result_layout)
        return result_gb

    def excel_name_bar(self):
        xl_gb = QGroupBox("Loaded Excel")
        xl_lay = QHBoxLayout()
        self._label_xl = QLabel("Case: ")
        xl_lay.addWidget(self._label_xl, Qt.AlignCenter)
        xl_gb.setLayout(xl_lay)
        return xl_gb
    def download_results(self):
        result_gb = QGroupBox("Save Results PDF")
        result_layout = QHBoxLayout()

        self.btn_open_download_pdf_selection = QPushButton("Save\nto\nPDF")
        self.btn_open_download_pdf_selection.setToolTip(
            "Downloads the results in the form of a pdf.")
        self.btn_open_download_pdf_selection.setIcon(QIcon(os.path.join(self._icons, "pdf.png")))

        self.btn_open_download_excel_selection = QPushButton("Save\nto\nExcel")
        self.btn_open_download_pdf_selection.setToolTip(
            "Downloads the results in the form of a Excel.")
        self.btn_open_download_pdf_selection.setIcon(QIcon(os.path.join(self._icons, "excel.png")))

        self.btn_open_download_csv_selection = QPushButton("Save\nto\nCSV")
        self.btn_open_download_csv_selection.setToolTip(
            "Downloads the results in the form of a csv.")
        self.btn_open_download_csv_selection.setIcon(QIcon(os.path.join(self._icons, "csv_icon.png")))


        result_layout.addWidget(self.btn_open_download_excel_selection)
        result_layout.addWidget(self.btn_open_download_csv_selection)
        result_layout.addWidget(self.btn_open_download_pdf_selection)

        result_gb.setLayout(result_layout)
        return result_gb
