import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtCore import QCoreApplication, QProcess, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QApplication, QTextEdit, QGridLayout, QWidget, \
    QHBoxLayout, QSizePolicy, QDockWidget, QTableWidget, QToolBar, QFileDialog, QTableWidgetItem

from Logger.log_streamer import log_parser
from Logger.subprocess_log_streamer import LogQueueReader
from controllers.commander import CommanderEPRA, Enumerations
from performance_report.AE_report import AEBaseExcelProcessor
from performance_report.HR_report import HRBaseExcelProcessor
from performance_report.PE_report import PEBaseExcelProcessor
from performance_report.SE_report import SEBaseExcelProcessor
from performance_report.admin_report import AdminBaseExcelProcessor
from performance_report.excel_process_one import process_excel
from ui.epra_contol_panel import EPRAControlPanel
from ui.ui_elements.file_folder_browser import FileFolderBrowser
from version_info import get_version
from general.general_functions import is_compiled, read_excel


class EPRASignals(QObject):
    signal_load_results_directory_started = pyqtSignal()
    signal_load_results_directory_finished = pyqtSignal()
    signal_load_base_excel_file_started = pyqtSignal()
    signal_load_base_excel_file_ended = pyqtSignal()
    signal_report_generation_started = pyqtSignal()
    signal_report_generation_finished = pyqtSignal()
    signal_save_results_to_pdf_started = pyqtSignal()
    signal_save_results_to_pdf_finished = pyqtSignal()


class EpraController:
    def __init__(self):
        self.signals = EPRASignals()
        self.action_in_progress = False
        self.commander = CommanderEPRA()
        # self.base_excel = self.commander._excel_dataframe
        # self.base_excel_headers = self.base_excel.columns.to_list()
        self._logger = logging.getLogger(__name__)

        log_queue_reader = LogQueueReader(self.commander.log_queue)
        log_queue_reader.start()

    def load_base_excel(self, path):
        basename, ext = os.path.splitext(str(path))
        if (ext == '.xlsx') or (ext == '.xls'):
            self.commander._base_excel_file = path
            return True
        else:
            return False

    # def load_results_dir(self, results_folder):
    #     if not os.path.exists(os.path.join(results_folder, "ERPFiles")):
    #         self._logger.debug("Creating 'EPRFiles' folder in {}".format(results_folder))
    #         os.mkdir(os.path.join(results_folder, "EPRFiles"))
    #     self.commander.results_folder = results_folder
    def load_results_dir(self, results_folder):
        erp_files_folder = os.path.join(results_folder, "ERPFiles")
        if not os.path.exists(erp_files_folder):
            self._logger.debug("Creating 'EPRFiles' folder in {}".format(results_folder))
            os.mkdir(erp_files_folder)
        else:
            self._logger.debug("'EPRFiles' folder already exists in {}".format(results_folder))
        self.commander.results_folder = results_folder

    def perform_report_generation(self):
        if not self.action_in_progress:
            self.action_in_progress = True
            self._report_generation = None  # TODO: define a method to complete the generation fo the report
            self._report_generation.signals.finished.connect(self._report_generation_completed)

    def _report_generation_completed(self):
        self.action_in_progress = False
        self.signals.signal_report_generation_finished.emit()

    def base_excel_writer_to_table(self, base_excel_table, result):
        row_count = base_excel_table.rowCount()
        base_excel_table.insertRow(row_count)
        try:
            for n, item in enumerate(result):
                base_excel_table.setItem(row_count, n, QTableWidget(str(item)))
            base_excel_table.resizeColumnsToContents()
            base_excel_table.resizeRowToContents(row_count)
            QApplication.processEvents()
        except:
            self._logger.error(
                "The table composer was unable to write {} to table, Please check the excel row in the file".format(
                    result))


class EPRA(QMainWindow):
    def __init__(self, controller):
        super(EPRA, self).__init__()
        self._controller = controller
        self.base_excel = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self.file_watcher = None

        # application_name, application_version = get_version()
        # self.setWindowTitle('Company Name Automated Report Generator (ver {})'.format(application_version))
        self.setWindowTitle('Company Name Automated Report Generator')
        self.setWindowIcon(QIcon(os.path.join(str(Path(__file__).parents[1]), "icons", "Logo.png")))
        self.setContentsMargins(0, 0, 0, 0)
        self.controls = EPRAControlPanel()
        self.console = QTextEdit()
        self.action_in_progress = False
        self._add_layouts()
        self._add_menus()
        self._add_console()
        self._add_top_toolbar()
        self.addToolBarBreak(Qt.TopToolBarArea)
        self._add_excel_toolbar()
        self.addToolBarBreak(Qt.TopToolBarArea)
        self._add_child_layouts_to_parent()
        self.showMaximized()
        self._logger.info("Started EPRA")

        # TODO: complete the below connections

        # self._controller.signals.signal_load_results_directory_started.connect(self)
        # self._controller.signals.signal_load_results_directory_finished.connect(self)
        self._controller.signals.signal_load_base_excel_file_started.connect(self._base_excel_file_fetching_started)
        self._controller.signals.signal_load_base_excel_file_ended.connect(self._base_excel_file_fetching_finished)
        self._controller.signals.signal_report_generation_started.connect(self._report_generation_started)
        self._controller.signals.signal_report_generation_finished.connect(self._report_generation_finished)
        self._controller.signals.signal_save_results_to_pdf_started.connect(self._results_to_pdf_started)
        self._controller.signals.signal_save_results_to_pdf_finished.connect(self._results_to_pdf_finished)

        sys.excepthook = self.custom_exception_hook
        self._initialize()

    def custom_exception_hook(self, exc_type, exc_value, exc_traceback):
        """
        Custom exception hook to log unhandled exceptions and display an error message.
        """
        self._logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

        if is_compiled():
            crash_file_path = os.path.join(getattr(sys, '_MEIPASS'), 'crash_file.txt')
        else:
            crash_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash_file.txt')
        with open(crash_file_path, 'a') as crash_file:
            # Log the complete traceback using the traceback module
            traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            crash_file.write(traceback_str)
            crash_file.write('\n' + '-' * 30 + '\n')
        # Display an error message to the user using QMessageBox
        error_message = "An unexpected error occurred. Crash details have been saved to '{}'.".format(crash_file_path)
        QMessageBox.critical(self, "Error", error_message, QMessageBox.Ok)

    def _add_layouts(self):
        self._parentlayout = QGridLayout()
        widget = QWidget()
        widget.setLayout(self._parentlayout)
        self.setCentralWidget(widget)
        self._layout1 = QHBoxLayout()
        self._base_excel_dock = QDockWidget("Excel Directory", self)
        self._results_dock = QDockWidget("Results Directory", self)

        self._main_dock = QMainWindow()
        self._main_dock.setFixedWidth(300)
        self._base_excel_tree = FileFolderBrowser(file_filter='*.xlsx',
                                                  icons=os.path.join(str(Path(__file__).parents[0]), "icons"),
                                                  message="Select base excel directory")
        self._base_excel_tree.fetchresult.connect(self._load_excel)
        self._results_tree = FileFolderBrowser(icons=os.path.join(str(Path(__file__).parents[0]), "icons"),
                                               file_browser=False,
                                               message="Select results directory")
        self._results_tree.fetchresult.connect(self._load_result_dir)

        self._base_excel_dock.setWidget(self._base_excel_tree)
        self._results_dock.setWidget(self._results_tree)
        self._main_dock.addDockWidget(Qt.LeftDockWidgetArea, self._base_excel_dock)
        self._main_dock.addDockWidget(Qt.LeftDockWidgetArea, self._results_dock)
        self._main_dock.tabifyDockWidget(self._base_excel_dock, self._results_dock)
        self._layout1.addWidget(self._main_dock)

        self._layout2 = QHBoxLayout()
        self._control_dock = QMainWindow()
        self._control_dock.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._execute_panel = QDockWidget("Execution Panel", self)
        self._base_excel_dock = QDockWidget("Raw Excel", self)

        self._base_excel_table = QTableWidget()
        self._base_excel_table.setSortingEnabled(True)
        self._reset_base_excel_table()
        self._base_excel_dock.setWidget(self._base_excel_table)

        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._execute_panel)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._base_excel_dock)
        self._control_dock.tabifyDockWidget(self._execute_panel, self._base_excel_dock)

        self._layout2.addWidget(self._control_dock)

    def _report_generation_started(self):
        self.controls.btn_open_generation_selection.setDisabled(True)

    def _report_generation_finished(self):
        self.controls.btn_open_generation_selection.setEnabled(True)

    def _base_excel_file_fetching_started(self):
        self.controls.btn_upload_excel.setDisabled(True)

    def _base_excel_file_fetching_finished(self):
        self.controls.btn_upload_excel.setEnabled(True)

    def _results_to_pdf_started(self):
        self.controls.btn_open_download_pdf_selection.setDisabled(True)

    def _results_to_pdf_finished(self):
        self.controls.btn_open_download_pdf_selection.setEnabled(True)

    def _add_console(self):
        self._execution_panel.setWidget(self.console)

    def _reset_base_excel_table(self):
        self._base_excel_table.clear()
        self._base_excel_table.setRowCount(0)
        # self._base_excel_table.setColumnCount(len(df_headers))
        # self._base_excel_table.setHorizontalHeaderLabels(df_headers)

    def _reset_base_excel_table1(self, df_headers):
        self._base_excel_table.clear()
        self._base_excel_table.setRowCount(0)
        self._base_excel_table.setColumnCount(len(df_headers))
        self._base_excel_table.setHorizontalHeaderLabels(df_headers)

    def _initialize(self):
        if self._controller.commander.excel_file:
            ret = self._base_excel_tree.set_path(self._controller.commander.excel_file)
            if not ret:
                self._logger.warning(
                    "Excel loading {} failed as mentioned path doesn't exist".format(
                        self._controller.commander.excel_file))
        if self._controller.commander.results_folder:
            self._logger.info("Assigning results directory as per given session")
            ret = self._results_tree.set_path(self._controller.commander.results_folder)
            if not ret:
                self._logger.warning(
                    "Results directory cannot be assigned as {} as mentioned path doesn't exist".format(
                        self._controller.commander.results_folder))
        self._initialize_designation_selection()

    def _initialize_designation_selection(self):
        if self._controller.commander.employee_designation == Enumerations.DesignationVer.ADMIN.value:
            self.controls.admin_radio.setChecked(True)
        elif self._controller.commander.employee_designation == Enumerations.DesignationVer.AE.value:
            self.controls.AE_radio.setChecked(True)
        elif self._controller.commander.employee_designation == Enumerations.DesignationVer.PE.value:
            self.controls.PE_radio.setChecked(True)
        elif self._controller.commander.employee_designation == Enumerations.DesignationVer.SE.value:
            self.controls.SE_radio.setChecked(True)
        elif self._controller.commander.employee_designation == Enumerations.DesignationVer.HR.value:
            self.controls.HR_radio.setChecked(True)

    def write_df_to_table(self, dataframe, table):
        if dataframe is not None:
            table.setRowCount(dataframe.shape[0])
            table.setColumnCount(dataframe.shape[1])
            table.setHorizontalHeaderLabels(dataframe.columns)

            for i in range(dataframe.shape[0]):
                for j in range(dataframe.shape[1]):
                    item = QTableWidgetItem(str(dataframe.iat[i,j]))
                    table.setItem(i,j,item)
            self._logger.info("Dataframe written to {}".format(table))
        else:
            self._logger.warning("Dataframe not found")
            QMessageBox.warning(self, "Warning", "No Excel file loaded.")

    def _load_excel(self, path):
        if path:
            # first checking is output directory has been assigned
            if not self._controller.commander.results_folder:
                QMessageBox.warning(self, "Warning", "Assign output directory first")
                self._logger.warning("Output directory not assigned")
                return
            else:
                if self._controller.load_base_excel(path):
                    self.controls.update_excel_label(path)
                    base_df = read_excel(path)
                    column_names_base_excel = base_df.columns.to_list()
                    # row_count = base_df.shape[0]
                    self._controller.commander.excel_file = path
                    self._reset_base_excel_table1(column_names_base_excel)
                    # for row in range(row_count):
                    #     self._controller.base_excel_writer_to_table(self._base_excel_table, base_df.loc[row, :].values.tolist())
                    self.write_df_to_table(base_df, self._base_excel_table)

                else:
                    QMessageBox.warning(self, "Warning", "Excel loading failed")

    def _load_result_dir(self, results_folder):
        # print("The function inside the second control panel is getting executed")
        if results_folder:
            self._controller.load_results_dir(results_folder)

    def _add_excel_toolbar(self):
        toolbarBox = QToolBar(self)
        self.addToolBar(Qt.BottomToolBarArea, toolbarBox)
        toolbarBox.addSeparator()
        toolbarBox.addWidget(self.controls.excel_name_bar())

    def _add_top_toolbar(self):
        toolbarBox = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbarBox)
        toolbarBox.addWidget(self.controls.designation_ver_selection())
        toolbarBox.addWidget(self.controls.generate_results())
        toolbarBox.addWidget(self.controls.download_results_pdf())
        self.controls.btn_open_generation_selection.clicked.connect(self._clickon_btn_main_run_generate_report)
        self.controls.btn_open_download_pdf_selection.clicked.connect(self._clickon_btn__save_results_to_pdf)

    def _add_excel_toolbar(self):
        toolbarBox = QToolBar(self)
        self.addToolBar(Qt.BottomToolBarArea, toolbarBox)
        toolbarBox.addSeparator()
        toolbarBox.addWidget(self.controls.excel_name_bar())

    def _add_child_layouts_to_parent(self):
        self._parentlayout.addLayout(self._layout1, 0, 0, 1, 1)
        self._parentlayout.addLayout(self._layout2, 0, 1, 1, 1)

    def _add_console(self):
        self._execute_panel.setWidget(self.console)

    def _add_menus(self):
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu('&File')

        self.action_browse_wdir = QAction('&Assign Results Directory...', self)
        self.action_browse_wdir.triggered.connect(self._results_tree.browse)

        self.action_browse_base_xl = QAction('&Assign Base Excel File', self)
        self.action_browse_base_xl.triggered.connect(self._base_excel_tree.browse)

        self.action_restart = QAction('&Restart (Ctrl+T)', self)
        self.action_restart.setShortcut('Ctrl+T')
        self.action_restart.setStatusTip('Restart  Application')
        self.action_restart.triggered.connect(self._restart_application)

        self.action_close = QAction('&Close (Ctrl+Q)', self)
        self.action_close.setShortcut('Ctrl+Q')
        self.action_close.setStatusTip('Close Application')
        self.action_close.triggered.connect(self._close_application)

        # Add menu actions in menu
        self.menu_file.addAction(self.action_browse_wdir)
        self.menu_file.addAction(self.action_browse_base_xl)
        self.menu_file.addAction(self.action_restart)
        self.menu_file.addAction(self.action_close)

    def _clickon_btn_upload_excel(self):
        app = QApplication([])
        self._controller.commander.excel_file, _ = QFileDialog.getOpenFileName(None, "Select Excel File", "",
                                                                               "Excel files (*.xlsx *.xls)")

    def _restart_application(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure to restart?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            QCoreApplication.quit()
            status = QProcess.startDetached(sys.executable, sys.argv)
        else:
            pass

    def _close_application(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            self._logger.warning("Quiting application")
            QApplication.quit()
        else:
            pass

    def _clickon_btn_main_run_generate_report(self):
        if self._controller.commander.results_folder is None:
            QMessageBox.information(self, 'Results Directory not available',
                                    "Browse results directory first")
        elif os.path.exists(self._controller.commander.results_folder):
            # print(self._controller.commander.excel_file)
            # print(self._controller.action_in_progress)
            if self._controller.commander.excel_file is not None and not self._controller.action_in_progress:
                base_df = read_excel(self._controller.commander.excel_file)
                dictionary_df = process_excel(base_df)
                if self._controller.commander.employee_designation == Enumerations.DesignationVer.ADMIN.value:
                    processor = AdminBaseExcelProcessor()
                    processor._input_dictionary = dictionary_df
                    # print(processor._input_dictionary)
                    processor._output_workbook_path = self._controller.commander.results_folder
                    processor.prepare_output_excel()
                elif self._controller.commander.employee_designation == Enumerations.DesignationVer.HR.value:
                    processor = HRBaseExcelProcessor()
                    processor._input_dictionary = dictionary_df
                    processor._output_workbook_path = self._controller.commander.results_folder
                    processor.prepare_output_excel()
                elif self._controller.commander.employee_designation == Enumerations.DesignationVer.AE.value:
                    processor = AEBaseExcelProcessor()
                    processor._input_dictionary = dictionary_df
                    processor._output_workbook_path = self._controller.commander.results_folder
                    processor.prepare_output_excel()
                elif self._controller.commander.employee_designation == Enumerations.DesignationVer.PE.value:
                    processor = PEBaseExcelProcessor()
                    processor._input_dictionary = dictionary_df
                    processor._output_workbook_path = self._controller.commander.results_folder
                    processor.prepare_output_excel()
                elif self._controller.commander.employee_designation == Enumerations.DesignationVer.SE.value:
                    processor = SEBaseExcelProcessor()
                    processor._input_dictionary = dictionary_df
                    processor._output_workbook_path = self._controller.commander.results_folder
                    processor.prepare_output_excel()
            else:
                QMessageBox.information(self, 'Operation Unsuccessful',
                                        "Please make it sure that Excel is set")

    def _clickon_btn__save_results_to_pdf(self):
        pass

    @pyqtSlot(object)
    def append_text(self, text):
        self.console.moveCursor(QTextCursor.End)
        for line in text.split("\n"):
            if line:
                self.console.append(log_parser(line))
