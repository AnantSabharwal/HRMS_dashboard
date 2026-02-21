import pandas as pd
from analysis.foundation import BasicAnalysis


class ByNameCalculator(BasicAnalysis):
    def __init__(self, df):
        """
        Initialize ByNameCalculator class.

        Args:
            df (DataFrame): Input DataFrame.
            columns_to_add (list): List of column names to add if missing. ['BD support', 'Studies/ Analysis (billable hours)',
             'Publications/ conferences/ panel discussions/ white papers/ webinars/ research',
             'People management (hiring/ mentoring/ engagement)','Trainings/ Self-development/ upskilling','Admin','Time-off']
            rows_to_add (list): List of row names to add if missing.
        """
        self._columns_to_add = ['BD support', 'Studies/ Analysis (billable hours)',
                                'Publications/ conferences/ panel discussions/ white papers/ webinars/ research',
                                'People management (hiring/ mentoring/ engagement)',
                                'Trainings/ Self-development/ upskilling', 'Admin', 'Time-off']
        self._rows_to_add = []
        super().__init__(df)
        self._total_duration_by_name = None
        self._grouped_df = None


    def _add_missing_columns(self):
        for col in self._columns_to_add:
            if col not in self._result_table.columns:
                self._result_table[col] = 0

    def _add_missing_rows(self):
        for row in self._rows_to_add:
            if row not in self._result_table.index:
                self._result_table.loc[row] = 0

    def get_total_duration(self):
        return self._total_duration_by_name

    def total_duration(self):
        self._total_duration_by_name = self._calculate_total_duration()

    def _group_data(self):
        self._grouped_df = self._df.groupby(['Name', 'Work Items'])['Duration'].sum().reset_index()
        return self._grouped_df

    def _calculate_total_duration(self):
        return self._df.groupby('Name')['Duration'].sum()

    def _generate_result_table(self):
        grouped_df = self._grouped_df.copy()
        grouped_df['Percentage'] = grouped_df.apply(
            lambda row: (row['Duration'] / self._total_duration_by_name[row['Name']]) * 100, axis=1)
        result_table = pd.pivot_table(grouped_df, values='Percentage', index='Name', columns='Work Items',
                                      fill_value=0)
        result_table['Total'] = result_table.sum(axis=1)
        self._result_table = result_table
