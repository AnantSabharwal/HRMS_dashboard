from enum import Enum

import pandas as pd

# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Markiv Consulting Services Inc.
"""
import multiprocessing
import os
from threading import Lock

from enum import Enum
from typing import List

import six


class CommanderMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances = {}

    _lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.

            if cls not in cls._instances:
                instance = super(CommanderMeta, cls).__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Enumerations:
    class DesignationVer(Enum):
        ADMIN = 1
        HR = 2
        AE = 3
        PE = 4
        SE = 5

    class DocumentType(Enum):
        Excel = 1
        Csv = 2
        PDF = 3
        JSON = 4

    class ProgramDecider:
        EPRA = 'EPRA'
        ETSRA = 'ETSRA'


class CommanderEPRA(object, six.with_metaclass(CommanderMeta)):
    def __init__(self, results_folder=None, excel_file=None,
                 employee_designation=Enumerations.DesignationVer.ADMIN.value, print_con_to_excel=True):
        self._base_data_folder = results_folder
        self._excel_file = excel_file
        self._employee_designation = employee_designation
        self._excel_dataframe = None
        self.log_queue = multiprocessing.Queue()
        self._results_folder = results_folder

    @property
    def excel_file(self):
        return self._excel_file

    @excel_file.setter
    def excel_file(self, path):
        # type: (os.path)  -> None
        if not isinstance(path, str):
            path = str(path)
        self._excel_file = path

    @property
    def results_folder(self):
        # type: () -> os.path
        return self._results_folder

    @results_folder.setter
    def results_folder(self, path):
        # type: (os.path)  -> None
        self._results_folder = path

    @property
    def excel_folder(self):
        # type: () -> os.path
        return self._results_folder

    @excel_folder.setter
    def excel_folder(self, path):
        # type: (os.path)  -> None
        self._base_data_folder = path

    @property
    def employee_designation(self):
        # type: (Enum) -> None
        return self._employee_designation

    @employee_designation.setter
    def employee_designation(self, ver):
        # type: (Enum) -> None
        self._employee_designation = ver

    def read_excel_to_dataframe(self):
        if self._base_excel_file is None:
            raise ValueError("Excel file path is not provided.")
        if not os.path.exists(self._base_excel_file):
            raise FileNotFoundError("Excel file does not exist at the provided path.")
        self._excel_dataframe = pd.read_excel(self._base_excel_file)


class CommanderETSRA(object, six.with_metaclass(CommanderMeta)):
    def __init__(self, base_excel_folder=None, timesheet_file=None, employee_information_file=None,processed_excel=None):
        self._base_excel_folder = base_excel_folder
        self._timesheet_file = timesheet_file
        self._employee_information_file = employee_information_file
        self.log_queue = multiprocessing.Queue()
        self._processed_excel = processed_excel
        self._overview_table = None
        self._designation_table = None
        self._location_table = None
        self._name_table = None
        self._service_table = None
        self._team_table = None
        self._report_generated = False

    @property
    def report_generated(self):
        return self._report_generated

    @report_generated.setter
    def report_generated(self, ans):
        self._report_generated = ans

    @property
    def overview_table(self):
        return self._overview_table

    @overview_table.setter
    def overview_table(self, tab):
        self._overview_table = tab

    @property
    def excel_folder(self):
        return self._base_excel_folder

    @excel_folder.setter
    def excel_folder(self, path):
        self._base_excel_folder = path

    @property
    def employee_timesheet(self):
        return self._timesheet_file

    @employee_timesheet.setter
    def employee_timesheet(self, path):
        self._timesheet_file = path

    @property
    def employee_information(self):
        return self._employee_information_file

    @employee_information.setter
    def employee_information(self, path):
        self._employee_information_file = path

    @property
    def excel_file_processed(self):
        return self._processed_excel

    @excel_file_processed.setter
    def excel_file_processed(self, df):
        self._processed_excel = df


if __name__ == "__main__":
    c2 = CommanderEPRA()
    print(c2.__dict__)
