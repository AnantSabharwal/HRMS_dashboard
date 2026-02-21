import sys
import time

import pandas as pd
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox


def read_csv(filename, skiprows=0):
    if sys.version_info[0] >= 3:
        return pd.read_csv(filename, skiprows=skiprows, on_bad_lines='skip')

    else:
        return pd.read_csv(filename, skiprows=skiprows, error_bad_lines=False)


def read_excel(filename, skiprows=0, header=0):
    return pd.read_excel(filename, skiprows=skiprows, header=header)  # , on_bad_lines='skip')


def is_compiled():
    """
    Check if the script is running as a compiled executable.
    """
    return getattr(sys, 'frozen', False)


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
    else:
        QMessageBox.warning(self, "Warning", "No Dataframe File Found.")
