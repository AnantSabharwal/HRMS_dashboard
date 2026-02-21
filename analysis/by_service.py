import pandas as pd
from analysis.foundation import BasicAnalysis


class ByServiceCalculator(BasicAnalysis):
    def __init__(self, df):
        """
        Initialize ByServiceCalculator class.

        Args: df (DataFrame): Input DataFrame.
        columns_to_add (list): -empty-
        rows_to_add (list): List of row names to add if missing. ['BD-Head',
            'Ops- Head- Utilities','Ops Head- Economics','Ops Head- Power Sys Studies & Equipment Modelling','Ops- Global
            Head','Ops-Regional Leads','Ops PE/TL','Ops SE','Ops AE']
        """
        super().__init__(df)
        self._total_duration_by_service = None
        self._grouped_df = None

    def get_total_duration(self):
        return self._total_duration_by_service

    def total_duration(self):
        self._total_duration_by_service = self._calculate_total_duration()

    def _group_data(self):
        self._grouped_df = self._df.groupby(['Category', 'Product_Service'])['Duration'].sum().reset_index()

    def _calculate_total_duration(self):
        return self._df.groupby('Category')['Duration'].sum()

    def _generate_result_table(self):
        grouped_df = self._grouped_df.copy()
        grouped_df['Percentage'] = grouped_df.apply(
            lambda row: (row['Duration'] / self._total_duration_by_service[row['Category']]) * 100, axis=1)
        result_table = pd.pivot_table(grouped_df, values='Percentage', index='Category', columns='Product_Service',
                                      fill_value=0)
        result_table['Total'] = result_table.sum(axis=1)
        self._result_table = result_table
