import os

import pandas as pd
import pyqtgraph as pg
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QComboBox, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton

from general.general_functions import write_df_to_table
from ui.ui_elements.chart_widget import create_pie_chart_widget


class NamePanelWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Analysis Based on Location")
        font = QFont()
        font.setBold(True)
        # internal df
        self._df = None
        self._grouped_df = None
        # layout for section1
        self._name_table = QTableWidget()
        self._name_table.setSortingEnabled(True)
        self._name_table_label = QLabel("Designation")
        self._reset_name_table()  # TODO: Add required functionality

        # graph widges
        self.main_tab_widget = QTabWidget()

        self.side_table_widget = QTableWidget()
        self.side_table_widget.setSortingEnabled(True)
        self.main_tab_widget.addTab(self.side_table_widget, "Name Specific")

        # graph widget
        self.graph_widget1 = QWidget()
        self.graph_widget1_layout = QVBoxLayout()
        self.graph_widget1.setLayout(self.graph_widget1_layout)
        self.main_tab_widget.addTab(self.graph_widget1, "Work Item Duration")

        # graph widget
        self.graph_widget2 = QWidget()
        self.graph_widget2_layout = QVBoxLayout()
        self.graph_widget2.setLayout(self.graph_widget2_layout)
        self.main_tab_widget.addTab(self.graph_widget2, "Product/Service Distribution")

        # graph widget
        self.graph_widget3 = QWidget()
        self.graph_widget3_layout = QVBoxLayout()
        self.graph_widget3.setLayout(self.graph_widget3_layout)
        self.main_tab_widget.addTab(self.graph_widget3, "Billable vs Non-Billable")

        self.dropdown_label = QLabel("Select Name")
        self.dropdown = QComboBox()
        employee_info_df = pd.read_excel(r"C:\Users\AnantSabharwal\pythonscripts\Admin_Dashboard_Parent\Admin_Dashboard_App\admin_dashboard_app\employee_mapping_sheet\employee_information.xlsx")
        names_list = employee_info_df['Name'].unique().tolist()
        for name in names_list:
            self.dropdown.addItem(name) # TODO : This should take a list of names of the various employees you can also take it according to the different employees that are present dynamically
        # dropdown.currentIndexChanged.connect(self.update_graphs_and_tables) # TODO : this function has to be defined

        self.plot_button = QPushButton("Analyze")
        self.plot_button.clicked.connect(self.update_graphs_and_tables)

        # layout for section 2
        _section2_layout = QVBoxLayout()
        _section2_layout.addWidget(self.dropdown_label)
        _section2_layout.addWidget(self.dropdown)
        _section2_layout.addWidget(self.plot_button)
        _section2_layout.addWidget(self.main_tab_widget)

        section2_container = QWidget()
        section2_container.setLayout(_section2_layout)

        # layout for whole window
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._name_table)
        main_layout.addWidget(section2_container)

        self.setLayout(main_layout)

    def update_graphs_and_tables(self):
        name = self.dropdown.currentText()
        self.side_table_widget.clear()
        name_data = self._df[self._df['Name'] == name]
        rows = self._grouped_df[self._grouped_df['Name'] == name]
        write_df_to_table(self, rows, self.side_table_widget)
        for i in reversed(range(self.graph_widget1_layout.count())):
            self.graph_widget1_layout.itemAt(i).widget().deleteLater()
            self.graph_widget2_layout.itemAt(i).widget().deleteLater()
            self.graph_widget3_layout.itemAt(i).widget().deleteLater()
        query1 = name_data.groupby('Work Items')['Duration'].sum()
        pie_widget1 = create_pie_chart_widget(query1, query1.index, title='Work Items Distribution for {}'.format(name))
        self.graph_widget1_layout.addWidget(pie_widget1)

        query2 = name_data.groupby('Product_Service')['Duration'].sum()
        pie_widget2 = create_pie_chart_widget(query2, query2.index,
                                              title='Product/Service Distribution for {}'.format(name))
        self.graph_widget2_layout.addWidget(pie_widget2)

        query3 = name_data.groupby('Billable')['Duration'].sum()
        pie_widget3 = create_pie_chart_widget(query3, query3.index,
                                              title='Billability for {}'.format(name))
        self.graph_widget3_layout.addWidget(pie_widget3)
        # pass

    def _reset_name_table(self):
        self._name_table.clear()
        self._name_table.setRowCount(0)

    @property
    def name_table(self):
        return self._name_table