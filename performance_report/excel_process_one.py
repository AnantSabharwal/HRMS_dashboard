import os
import pandas as pd
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel
import xlsxwriter


def process_excel(df):
    result_dict_list = df.set_index('Name').to_dict(orient='index')
    return result_dict_list

#
# class ExcelProcessorOne:
#     def __init__(self):
#         self.file_path = None
#         self.result_dict_list = None
#         self.excel_file_path = None
#
#     def get_new_filename(self, base_filename, count=1):
#         filename, extension = os.path.splitext(base_filename)
#         new_filename = "{}_{}{}".format(filename, count, extension)
#         return new_filename
#
#     def select_file(self):
#         app = QApplication([])
#         self.file_path, _ = QFileDialog.getOpenFileName(None, "Select Excel File", "", "Excel files (*.xlsx *.xls)")
#         if self.file_path:
#             self.process_excel()
#
#     def process_excel(self):
#         df = pd.read_excel(self.file_path)
#         self.result_dict_list = df.set_index('Name').to_dict(orient='index')
#         return self.result_dict_list
#         print(self.result_dict_list)
#         desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
#         self.excel_file_path = 'output_file.xlsx'
#         count = 1
#         while os.path.exists(os.path.join(desktop_path, self.excel_file_path)):
#             self.excel_file_path = self.get_new_filename('output_file.xlsx', count)
#             count += 1
#
#         with pd.ExcelWriter(self.excel_file_path, engine='xlsxwriter') as writer:
#             for sheet_name, row_dict in self.result_dict_list.items():
#                 sheet_df = pd.DataFrame.from_dict(row_dict, orient='index')
#                 sheet_df.to_excel(writer, sheet_name=sheet_name)
#
#     def get_output_message(self):
#         if self.excel_file_path:
#             return f"Processing complete. Output file saved to Desktop as {self.excel_file_path}"
#         else:
#             return "No file selected."
#
#
# # Example of usage
# if __name__ == "__main__":
#     excel_processor = ExcelProcessorOne()
#     excel_processor.select_file()
#     output_message = excel_processor.get_output_message()
#     print(output_message)
