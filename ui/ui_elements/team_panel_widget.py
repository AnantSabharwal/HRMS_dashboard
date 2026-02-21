import os

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QComboBox, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from preprocessing.mapping_static import team_mapping
from general.general_functions import write_df_to_table
from ui.ui_elements.chart_widget import create_pie_chart_widget


class TeamPanelWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Analysis Based on Team")
        font = QFont()
        font.setBold(True)
        # internal df
        self._df = None
        self._grouped_df = None
        # layout for section1
        self._team_table = QTableWidget()
        self._team_table.setSortingEnabled(True)
        self._team_table_label = QLabel("Team")
        self._reset_team_table()

        # graph widges
        self.main_tab_widget = QTabWidget()

        self.side_table_widget = QTableWidget()
        self.side_table_widget.setSortingEnabled(True)
        self.main_tab_widget.addTab(self.side_table_widget, "Team Specific")

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

        self.dropdown_label = QLabel("Select Team")
        self.dropdown = QComboBox()
        employee_info_df = pd.read_excel(
            r"C:\Users\AnantSabharwal\pythonscripts\Admin_Dashboard_Parent\Admin_Dashboard_App\admin_dashboard_app\employee_mapping_sheet\employee_information.xlsx")
        team_list = employee_info_df['Team'].unique().tolist()
        for team in team_list:
            self.dropdown.addItem(str(team))
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
        main_layout.addWidget(self._team_table)
        main_layout.addWidget(section2_container)

        self.setLayout(main_layout)

    def update_graphs_and_tables(self):
        team = self.dropdown.currentText()
        self.side_table_widget.clear()
        team_data = self._df[self._df['Team'] == team]
        rows = self._grouped_df[self._grouped_df['Team'] == team]
        write_df_to_table(self, rows, self.side_table_widget)
        for i in reversed(range(self.graph_widget1_layout.count())):
            self.graph_widget1_layout.itemAt(i).widget().deleteLater()
            self.graph_widget2_layout.itemAt(i).widget().deleteLater()
            self.graph_widget3_layout.itemAt(i).widget().deleteLater()

        query1 = team_data.groupby('Work Items')['Duration'].sum()
        pie_widget1 = create_pie_chart_widget(query1, query1.index, title='Work Items Distribution for {}'.format(team))
        self.graph_widget1_layout.addWidget(pie_widget1)

        query2 = team_data.groupby('Product_Service')['Duration'].sum()
        pie_widget2 = create_pie_chart_widget(query2, query2.index,
                                                   title='Product/Service Distribution for {}'.format(team))
        self.graph_widget2_layout.addWidget(pie_widget2)

        query3 = team_data.groupby('Billable')['Duration'].sum()
        pie_widget3 = create_pie_chart_widget(query3, query3.index,
                                              title='Billability for {}'.format(team))
        self.graph_widget3_layout.addWidget(pie_widget3)

    def _reset_team_table(self):
        self._team_table.clear()
        self._team_table.setRowCount(0)

    @property
    def team_table(self):
        return self._team_table