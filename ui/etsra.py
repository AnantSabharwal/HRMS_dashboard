import logging
import os
import re
import sys
import traceback
import typing
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtCore import QCoreApplication, QProcess, Qt, QObject, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox, QApplication, QTextEdit, QGridLayout, QWidget, \
    QHBoxLayout, QDockWidget, QSizePolicy, QTableWidget, QToolBar, QTableWidgetItem, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from openpyxl.writer.excel import ExcelWriter

from Logger.log_streamer import log_parser
from Logger.subprocess_log_streamer import LogQueueReader
from analysis.by_designation import ByDesignationCalculator
from analysis.by_location import ByLocationCalculator
from analysis.by_name import ByNameCalculator
from analysis.by_service import ByServiceCalculator
from analysis.by_team import ByTeamCalculator
from analysis.overview import OverviewCalculator
from controllers.commander import CommanderETSRA
from general.general_functions import is_compiled, read_excel
from preprocessing.data_preprocessing import dataframe_processing
from ui.ui_elements.designation_panel_widget import DesignationPanelWidget
from ui.ui_elements.file_folder_browser import FileFolderBrowser
from ui.ui_elements.location_panel_widget import LocationPanelWidget
from ui.ui_elements.name_panel_widget import NamePanelWidget
from ui.ui_elements.overview_table_widget import OverviewWidget
from ui.ui_elements.service_panel_widget import ServicePanelWidget
from ui.ui_elements.team_panel_widget import TeamPanelWidget
from version_info import get_version
from ui.etsra_control_panel import ETSRAControlPanel


class ETSRASignals(QObject):
    signal_load_base_excel_folder_started = pyqtSignal()
    signal_load_base_excel_folder_ended = pyqtSignal()
    signal_run_started = pyqtSignal()
    signal_run_finished = pyqtSignal()


class EtsraController:
    def __init__(self):
        self.signals = ETSRASignals()
        self.action_in_progress = False
        self.commander = CommanderETSRA()
        self._logger = logging.getLogger(__name__)

        log_queue_reader = LogQueueReader(self.commander.log_queue)
        log_queue_reader.start()

    # def load_base_excel(self, path):
    #     basename, ext = os.path.splitext(str(path))
    #     if (ext == '.xlsx') or (ext == '.xls'):
    #         self.commander._base_excel_file = path
    #         return True
    #     else:
    #         return False

    def load_base_excel_dir(self, excel_folder):
        # if not os.path.exists(os.path.join(excel_folder, "TimeSheetFiles")):
        if not os.path.exists(excel_folder):
            self._logger.debug(
                "Expected folder doesn't exist")  # . Please add the files in a folder 'TimeSheetFiles' ")
        else:
            self.commander.timesheet_excel_file = self._assign_timesheet_excel_file(excel_folder)
            self.commander.employee_info_file = self._assign_employee_info_file(excel_folder)
            self.commander.base_excel_folder = excel_folder
            return read_excel(self.commander.timesheet_excel_file, skiprows=4, header=0), read_excel(
                self.commander.employee_info_file)

    # def _assign_timesheet_excel_file(self, excel_folder):
    #     pattern = r'Company Name,\+LLC_Time\+Activities\+by\+\+Employee\+Detail\s\(\d+\).(xlsx|xls)'
    #     timesheet_folder = excel_folder #os.path.join(excel_folder, 'TimeSheetFiles')
    #     timesheet_files = os.listdir(timesheet_folder)
    #     for file_name in timesheet_files:
    #         if re.search(pattern, file_name):
    #             self._logger.info("An already present file has been found and selected")
    #             return os.path.join(timesheet_folder, file_name)
    #     self._logger.info("No file found of the pattern searched")
    #     return None
    # #TODO: Add functionality to deal with multiple files

    def display_list_and_get_input(self, items):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Select a File")
        msgBox.setText("Choose an file from the list:")

        buttons = []
        for item in items:
            msgBox.addButton(msgBox.addButton(item, QMessageBox.ActionRole))
        msgBox.exec_()
        for button in buttons:
            if msgBox.clickedButton() == button:
                selected_item = button.text()
                return selected_item
                break
        else:
            self._logger.info("No file selected")

    def _assign_timesheet_excel_file(self, excel_folder):
        pattern = r'Company Name,\+LLC_Time\+Activities\+by\+\+Employee\+Detail\s\(\d+\).(xlsx|xls)'
        # timesheet_folder = os.path.join(excel_folder, 'TimeSheetFiles')
        timesheet_folder = excel_folder
        timesheet_files = os.listdir(timesheet_folder)
        matching_files = [f for f in timesheet_files if re.search(pattern, f)]
        print(matching_files)
        if len(matching_files) > 1:
            self._logger.info("Matching files have been found:")
            for i, file_name in enumerate(matching_files):
                self._logger.info("{}. {}".format(i + 1, file_name))
            while True:
                try:
                    choice = self.display_list_and_get_input(matching_files)
                    # choice = int(input("Enter the number corresponding to the file you want to select: "))
                    if 1 <= choice <= len(matching_files):
                        selected_file = os.path.join(timesheet_folder, matching_files[choice - 1])
                        self._logger.info("File selected: %s" % selected_file)
                        return selected_file
                    else:
                        self._logger.info(
                            "Invalid choice. Please enter a number between 1 and %d" % len(matching_files))
                except ValueError:
                    self._logger.info("Invalid input. Please enter a number.")
            self._logger.info("No file found of the pattern searched")
            return None
        elif len(matching_files) == 1:
            selected_file = os.path.join(timesheet_folder, matching_files[0])
            self._logger.info("File selected: %s" % selected_file)
            return selected_file
        else:
            self._logger.debug("No timesheet file of the pattern {} found".format(pattern))

    def _assign_employee_info_file(self, excel_folder):
        employee_information_file = os.path.join(excel_folder, "employee_information.xlsx")  # "TimeSheetFiles",
        if not os.path.exists(employee_information_file):
            self._logger.info("employee_information.xlsx not found. Taking inbuilt version")
            employee_information_file = os.path.join(str(Path(__file__).parents[1]), "employee_mapping_sheet",
                                                     "employee_information.xlsx")
            self._logger.info("Static employee information sheet seleted.")
            return employee_information_file
        self._logger.info("Employee information sheet set")
        return employee_information_file

    def perform_result_generation(self):
        if not self.action_in_progress:
            self.action_in_progress = True
            self._result_generation = None  # TODO: define a method to complete the generation fo the report
            self._result_generation.signals.finished.connect(self._report_generation_completed)

    def _report_generation_completed(self):
        self.action_in_progress = False
        self.signals.signal_report_generation_finished.emit()

    @pyqtSlot()
    def dataframe_writer_to_table(self, base_excel_table, result):
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


class ETSRA(QMainWindow):
    def __init__(self, controller):
        super(ETSRA, self).__init__()
        self._controller = controller
        self._logger = logging.getLogger(self.__class__.__name__)
        # application_name, application_version = get_version()
        # self.setWindowTitle('Company Name Automated Report Generator (ver {})'.format(application_version))
        self.setWindowTitle('Company Name Automated Report Generator')
        self.setWindowIcon(QIcon(os.path.join(str(Path(__file__).parents[1]), "icons", "Logo.png")))
        self.setContentsMargins(0, 0, 0, 0)
        self.controls = ETSRAControlPanel()
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
        self._logger.info("Started ETSRA")

        self._controller.signals.signal_load_base_excel_folder_started.connect(self._base_excel_folder_fetching_started)
        self._controller.signals.signal_load_base_excel_folder_started.connect(
            self._base_excel_folder_fetching_finished)
        self._controller.signals.signal_run_started.connect(self._run_started)
        self._controller.signals.signal_run_finished.connect(self._run_finished)

        sys.excepthook = self.custom_exception_hook
        self._initialize()

    def _base_excel_folder_fetching_started(self):
        self.controls.btn_assign_excel_directory.setDisabled(True)

    def _base_excel_folder_fetching_finished(self):
        self.controls.btn_assign_excel_directory.setEnabled(True)

    def _run_started(self):
        self.controls.btn_open_generation_selection.setDisabled(True)

    def _run_finished(self):
        self.controls.btn_open_generation_selection.setEnabled(True)

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
        self._parent_layout = QGridLayout()
        widget = QWidget()
        widget.setLayout(self._parent_layout)
        self.setCentralWidget(widget)

        self._layout1 = QHBoxLayout()
        self._base_excel_dock = QDockWidget('Excel Directory', self)
        self._main_dock = QMainWindow()
        screen_geometry = QApplication.desktop().screenGeometry()
        fixed_width = screen_geometry.width() * 0.2
        self._main_dock.setFixedWidth(fixed_width)

        self._base_excel_dir_tree = FileFolderBrowser(file_browser=False,  # file_filter='*.xlsx',
                                                      icons=os.path.join(str(Path(__file__).parents[0]), "icons"),
                                                      message="Select base excel directory")
        self._base_excel_dir_tree.fetchresult.connect(self._load_base_excel_dir)

        self._base_excel_dock.setWidget(self._base_excel_dir_tree)
        self._main_dock.addDockWidget(Qt.LeftDockWidgetArea, self._base_excel_dock)
        # self._main_dock.tabifyDockWidget(self._base_excel_dock, None)
        self._layout1.addWidget(self._main_dock)

        self._layout2 = QHBoxLayout()
        self._control_dock = QMainWindow()
        self._control_dock.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self._execute_panel = QDockWidget("Execution Panel", self)
        self._base_excel_dock = QDockWidget("Raw Excel", self)
        self._formatted_excel_dock = QDockWidget("Formatted Excel", self)
        self._overview_dock = QDockWidget("Overview", self)
        self._designation_dock = QDockWidget("Designation", self)
        self._location_dock = QDockWidget("Location", self)
        self._name_dock = QDockWidget("Name", self)
        self._service_dock = QDockWidget("Service", self)
        self._team_dock = QDockWidget("Team", self)

        # raw excel table
        self._base_excel_table = QTableWidget()
        self._base_excel_table.setSortingEnabled(True)
        self._reset_base_excel_table()
        self._base_excel_dock.setWidget(self._base_excel_table)

        # formatted excel table
        self._formatted_excel_table = QTableWidget()
        self._formatted_excel_table.setSortingEnabled(True)
        self._reset_formatted_excel_table()
        self._formatted_excel_dock.setWidget(self._formatted_excel_table)

        # overview dock
        self._overview_widget = OverviewWidget()
        self._overview_dock.setWidget(self._overview_widget)
        self._overview_widget.setDisabled(False)

        # designation dock
        self._designation_panel_widget = DesignationPanelWidget()
        self._designation_dock.setWidget(self._designation_panel_widget)
        self._designation_dock.setDisabled(False)

        # location dock
        self._location_panel_widget = LocationPanelWidget()
        self._location_dock.setWidget(self._location_panel_widget)
        self._location_dock.setDisabled(False)

        # name dock
        self._name_panel_widget = NamePanelWidget()
        self._name_dock.setWidget(self._name_panel_widget)
        self._name_dock.setDisabled(False)

        # service dock
        self._service_panel_widget = ServicePanelWidget()
        self._service_dock.setWidget(self._service_panel_widget)
        self._service_dock.setDisabled(False)

        # team dock
        self._team_panel_widget = TeamPanelWidget()
        self._team_dock.setWidget(self._team_panel_widget)
        self._team_dock.setDisabled(False)

        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._execute_panel)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._base_excel_dock)
        self._control_dock.tabifyDockWidget(self._execute_panel, self._base_excel_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._formatted_excel_dock)
        self._control_dock.tabifyDockWidget(self._base_excel_dock, self._formatted_excel_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._overview_dock)
        self._control_dock.tabifyDockWidget(self._formatted_excel_dock, self._overview_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._designation_dock)
        self._control_dock.tabifyDockWidget(self._overview_dock, self._designation_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._location_dock)
        self._control_dock.tabifyDockWidget(self._designation_dock, self._location_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._name_dock)
        self._control_dock.tabifyDockWidget(self._location_dock, self._name_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._service_dock)
        self._control_dock.tabifyDockWidget(self._name_dock, self._service_dock)
        self._control_dock.addDockWidget(Qt.TopDockWidgetArea, self._team_dock)
        self._control_dock.tabifyDockWidget(self._service_dock, self._team_dock)
        self._layout2.addWidget(self._control_dock)

    def _add_top_toolbar(self):
        toolbarBox = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbarBox)
        toolbarBox.addWidget(self.controls.assign_results_directory())
        toolbarBox.addWidget(self.controls.generate_results())
        toolbarBox.addWidget(self.controls.download_results())
        self.controls.btn_assign_excel_directory.clicked.connect(self._load_base_excel_dir)
        self.controls.btn_open_generation_selection.clicked.connect(self._clickon_generate_report)
        self.controls.btn_open_download_excel_selection.clicked.connect(self._clickon_save_results_to_excel)
        self.controls.btn_open_download_csv_selection.clicked.connect(self._clickon_save_results_to_csv)
        self.controls.btn_open_download_pdf_selection.clicked.connect(self._clickon_btn__save_results_to_pdf)

    def _reset_formatted_excel_table(self):
        self._formatted_excel_table.clear()
        self._formatted_excel_table.setRowCount(0)

    def _reset_base_excel_table(self):
        self._base_excel_table.clear()
        self._base_excel_table.setRowCount(0)

    def _add_excel_toolbar(self):
        toolbarBox = QToolBar(self)
        self.addToolBar(Qt.BottomToolBarArea, toolbarBox)
        toolbarBox.addSeparator()
        toolbarBox.addWidget(self.controls.excel_name_bar())

    def _add_child_layouts_to_parent(self):
        self._parent_layout.addLayout(self._layout1, 0, 0, 1, 1)
        self._parent_layout.addLayout(self._layout2, 0, 1, 1, 1)

    def _add_console(self):
        self._execute_panel.setWidget(self.console)

    def _add_menus(self):
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu('&File')

        self.action_browse_wdir = QAction('&Browse File Directory...', self)
        self.action_browse_wdir.triggered.connect(self._base_excel_dir_tree.browse)

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
        self.menu_file.addAction(self.action_restart)
        self.menu_file.addAction(self.action_close)

    def _initialize(self):
        if self._controller.commander._base_excel_folder:
            self._logger.info("Assigning Excel directory as per given session")
            ret = self._base_excel_dir_tree.set_path(self._controller.commander._base_excel_folder)
            if not ret:
                self._logger.warning(
                    "Results directory cannot be assigned as {} as mentioned path doesn't exist".format(
                        self._controller.commander._base_excel_folder))

    def _load_base_excel_dir(self, excel_folder):
        if excel_folder:
            self._controller.commander._base_excel_folder = excel_folder
            raw_timesheet_df, employee_df = self._controller.load_base_excel_dir((str(excel_folder)))
            self._reset_base_excel_table()
            row_count = raw_timesheet_df.shape[0]
            # for row in range(row_count):
            #     self._controller.dataframe_writer_to_table(self._base_excel_table, raw_timesheet_df.loc[row, :].values.tolist())
            self.write_df_to_table(raw_timesheet_df, self._base_excel_table)

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

    def write_df_to_table(self, df, table):
        dataframe = df
        if dataframe is not None:
            table.setRowCount(dataframe.shape[0])
            table.setColumnCount(dataframe.shape[1])
            table.setHorizontalHeaderLabels(dataframe.columns)

            for i in range(dataframe.shape[0]):
                for j in range(dataframe.shape[1]):
                    item = QTableWidgetItem(str(dataframe.iat[i, j]))
                    table.setItem(i, j, item)
            self._logger.info("Dataframe written to {}".format(table))
        else:
            self._logger.warning("Dataframe not found")
            QMessageBox.warning(self, "Warning", "No Dataframe File Found.")

    def write_df_to_table_T(self, dataframe, table):
        df = dataframe.T
        if df is not None:
            table.setRowCount(df.shape[0])
            table.setColumnCount(df.shape[1] + 1)

            # Set header labels
            header_labels = ["Index"] + list(df.columns)
            table.setHorizontalHeaderLabels(header_labels)

            for i, (idx, row) in enumerate(df.iterrows()):
                table.setItem(i, 0, QTableWidgetItem(str(idx)))
                for j, val in enumerate(row):
                    table.setItem(i, j + 1, QTableWidgetItem(str(val)))
            self._logger.info("Pivot table written to {}".format(table))
        else:
            self._logger.warning("Pivot table not found")
            QMessageBox.warning(self, "Warning", "No Pivot Table Found.")

    def _clickon_generate_report(self):
        if self._controller.commander.timesheet_excel_file is not None:
            if self._controller.commander.employee_info_file is not None:
                self._controller.commander._processed_excel = dataframe_processing(
                    self._controller.commander.timesheet_excel_file, self._controller.commander.employee_info_file)
                self.write_df_to_table(self._controller.commander._processed_excel, self._formatted_excel_table)

                self.local_processed_excel = self._controller.commander._processed_excel

                # overview panel
                self._controller.commander._overview_table = OverviewCalculator(
                    self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._overview_table._result_table,
                                         self._overview_widget._overview_table)
                overview_graph1_query = self.local_processed_excel[self.local_processed_excel['Billable']=='Yes'].groupby('Client')['Amount'].sum()
                overview_graph2_query = self.local_processed_excel.groupby('Work Items')['Duration'].sum()
                first_elements = {key: value for key, value in overview_graph2_query.items()}
                labels_list = []
                for key, value in first_elements.items():
                    labels_list.append((key))
                self._overview_widget.update_graph_widget1(overview_graph1_query, x_label='Client', y_label='Amount',title='Client vs Amount')
                self._overview_widget.update_graph_widget2(overview_graph2_query,labels=labels_list, title='Work Item Duration Distribution')

                # team panel
                self._controller.commander._team_table = ByTeamCalculator(self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._team_table._result_table,
                                         self._team_panel_widget._team_table)
                self._team_panel_widget._df = self.local_processed_excel
                self._team_panel_widget._grouped_df = self._controller.commander._team_table._group_data()

                # designation panel
                self._controller.commander._designation_table = ByDesignationCalculator(
                    self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._designation_table._result_table,
                                         self._designation_panel_widget._designation_table)
                self._designation_panel_widget._df = self.local_processed_excel
                self._designation_panel_widget._grouped_df = self._controller.commander._designation_table._group_data()

                # location panel
                self._controller.commander._location_table = ByLocationCalculator(
                    self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._location_table._result_table,
                                         self._location_panel_widget._location_table)
                self._location_panel_widget._df = self.local_processed_excel
                self._location_panel_widget._grouped_df = self._controller.commander._location_table._group_data()

                # name panel
                self._controller.commander._name_table = ByNameCalculator(self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._name_table._result_table,
                                         self._name_panel_widget._name_table)
                self._name_panel_widget._df = self.local_processed_excel
                self._name_panel_widget._grouped_df = self._controller.commander._name_table._group_data()

                #service panel
                self._controller.commander._service_table = ByServiceCalculator(
                    self._controller.commander._processed_excel)
                self.write_df_to_table_T(self._controller.commander._service_table._result_table,
                                         self._service_panel_widget._service_table)

                self._controller.commander._report_generated = True
            else:
                self._logger.warning("Employee information file not found")
        else:
            self._logger.warning("Timesheet file not found, Please upload")
            QMessageBox.warning(None, "Warning", "Upload the timesheet file", QMessageBox.Ok)

    def _clickon_save_results_to_excel(self):
        if self._controller.commander.report_generated:
            self._logger.info("Saving to excel started")
            # writer = ExcelWriter(
            #     os.path.join(self._controller.commander.base_excel_folder, "Employee_Timesheet_Report.xlsx"))
            writer = pd.ExcelWriter(os.path.join(self._controller.commander.base_excel_folder, "Employee_Timesheet_Report.xlsx"), engine="xlsxwriter")
            self._controller.commander._processed_excel.to_excel(writer, 'Processed Excel')
            self._controller.commander._overview_table._result_table.to_excel(writer, 'Overview')
            self._controller.commander._name_table._result_table.to_excel(writer, 'Name')
            self._controller.commander._location_table._result_table.to_excel(writer, 'Location')
            self._controller.commander._team_table._result_table.to_excel(writer, 'Team')
            self._controller.commander._designation_table._result_table.to_excel(writer, 'Designation')
            self._controller.commander._service_table._result_table.to_excel(writer, 'Service')
            writer.save()
            self._logger.info("Saving to excel completed")

    def _clickon_save_results_to_csv(self):
        if self._controller.commander.report_generated:
            self._logger.info("Saving to CSV started")
            base_folder = self._controller.commander.base_excel_folder
            self._controller.commander._processed_excel.to_csv(os.path.join(base_folder, "Processed_Excel.csv"), index=False)
            self._controller.commander._overview_table._result_table.to_csv(os.path.join(base_folder, "Overview.csv"), index=False)
            self._controller.commander._name_table._result_table.to_csv(os.path.join(base_folder, "Name.csv"), index=False)
            self._controller.commander._location_table._result_table.to_csv(os.path.join(base_folder, "Location.csv"), index=False)
            self._controller.commander._team_table._result_table.to_csv(os.path.join(base_folder, "Team.csv"), index=False)
            self._controller.commander._designation_table._result_table.to_csv(os.path.join(base_folder, "Designation.csv"), index=False)
            self._controller.commander._service_table._result_table.to_csv(os.path.join(base_folder, "Service.csv"), index=False)
            self._logger.info("Saving to CSV completed")
    def _clickon_btn__save_results_to_pdf(self):
        pass

    @pyqtSlot(object)
    def append_text(self, text):
        self.console.moveCursor(QTextCursor.End)
        for line in text.split("\n"):
            if line:
                self.console.append(log_parser(line))
