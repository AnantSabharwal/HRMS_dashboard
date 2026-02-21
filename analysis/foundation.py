import pandas as pd
from abc import ABC, abstractmethod


class BasicAnalysis:
    def __init__(self, df):
        """
        Initialize BasicAnalysis class.

        Args:
            df (DataFrame): Input DataFrame.
            columns_to_add (list): List of column names to add if missing.
            rows_to_add (list): List of row names to add if missing.
        """
        self._df = df
        # self._columns_to_add = None
        # self._rows_to_add = None
        self._result_table = None
        # self._result_table_t = None
        self.prepare_results_table()

    @property
    def dataframe(self):
        return self._df

    @dataframe.setter
    def dataframe(self, df):
        self._df = df

    # @property
    # def cols_to_add(self):
    #     return self._columns_to_add
    #
    # @cols_to_add.setter
    # def cols_to_add(self, column_list):
    #     self._columns_to_add = column_list
    #
    # @property
    # def rows_to_add(self):
    #     return self._rows_to_add
    #
    # @rows_to_add.setter
    # def rows_to_add(self, rows_list):
    #     self._rows_to_add = rows_list

    def input_dataframe_present(self):
        if self._df is not None:
            return True
        else:
            return False

    def _add_missing_columns(self):
        pass
        # for col in self._columns_to_add:
        #     if col not in self._result_table.columns:
        #         self._result_table[col] = 0

    def _add_missing_rows(self):
        pass
        # for row in self._rows_to_add:
        #     if row not in self._result_table.index:
        #         self._result_table.loc[row] = 0

    def _group_data(self):
        pass

    def total_duration(self):
        pass

    def _generate_result_table(self):
        pass

    def display_result(self):
        """
        Display the result table.
        """
        return self._result_table.T

    def prepare_results_table(self):
        if self.input_dataframe_present():
            # print(self.input_dataframe_present())
            self._group_data()
            self.total_duration()
            self._generate_result_table()
            self._add_missing_columns()
            self._add_missing_rows()
            self.display_result()



