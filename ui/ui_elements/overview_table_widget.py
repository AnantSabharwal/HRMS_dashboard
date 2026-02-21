import os

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QHBoxLayout, QTabWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QTableWidget, QHeaderView
from matplotlib.figure import Figure

from ui.ui_elements.chart_widget import create_pie_chart_widget, create_bar_graph_widget


class OverviewWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Overview")
        font = QFont()
        font.setBold(True)

        self._overview_table = QTableWidget()
        self._overview_table.setSortingEnabled(True)
        self._overview_table_label = QLabel("Overview")
        self._reset_overview_table()
        self._overview_table_label.setFont(font)

        # Enable scrolling for the table widget
        self._overview_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._overview_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        graph_tab_widget = QTabWidget()

        self.graph_widget1 = QWidget()
        self.graph_widget1_layout = QVBoxLayout()  # Layout for graph_widget1
        self.graph_widget1.setLayout(self.graph_widget1_layout)

        self.graph_widget2 = QWidget()
        self.graph_widget2_layout = QVBoxLayout()  # Layout for graph_widget2
        self.graph_widget2.setLayout(self.graph_widget2_layout)

        graph_tab_widget.addTab(self.graph_widget1, "Billable Amt Per Client")
        graph_tab_widget.addTab(self.graph_widget2, "Work Item Time Spent")

        section2_layout = QVBoxLayout()
        section2_layout.addWidget(graph_tab_widget)

        section2_container = QWidget()
        section2_container.setLayout(section2_layout)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self._overview_table)
        self.main_layout.addWidget(section2_container)
        self.setLayout(self.main_layout)  # Set main layout for the widget

        # Save references to graph_widget1 and graph_widget2 for easy access
        self.graph_widget1_ref = self.graph_widget1
        self.graph_widget2_ref = self.graph_widget2

    def _reset_overview_table(self):
        self._overview_table.clear()
        self._overview_table.setRowCount(0)

    def update_graph_widget1(self, data, x_label='X Label', y_label='Y Label', title='Bar Graph'):
        for i in reversed(range(self.graph_widget1_layout.count())):
            self.graph_widget1_layout.itemAt(i).widget().deleteLater()
        bar_widget = create_bar_graph_widget(data, x_label, y_label, title)
        self.graph_widget1_layout.addWidget(bar_widget)

    def update_graph_widget2(self, data, labels, title='Pie Chart'):
        for i in reversed(range(self.graph_widget2_layout.count())):
            self.graph_widget2_layout.itemAt(i).widget().deleteLater()
        # Create new pie chart widget
        pie_widget = create_pie_chart_widget(data, labels, title)
        self.graph_widget2_layout.addWidget(pie_widget)

