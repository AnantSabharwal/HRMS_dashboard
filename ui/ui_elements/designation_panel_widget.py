import os
import pyqtgraph as pg
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QComboBox, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton

from general.general_functions import write_df_to_table
from ui.ui_elements.chart_widget import create_pie_chart_widget


class DesignationPanelWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Analysis Based on Designation")
        font = QFont()
        font.setBold(True)
        # internal df
        self._df = None
        self._grouped_df = None
        # layout for section1
        self._designation_table = QTableWidget()
        self._designation_table.setSortingEnabled(True)
        self._designation_table_label = QLabel("Designation")
        self._reset_designation_table()  # TODO: Add required functionality

        # graph widges
        self.main_tab_widget = QTabWidget()

        self.side_table_widget = QTableWidget()
        self.side_table_widget.setSortingEnabled(True)
        self.main_tab_widget.addTab(self.side_table_widget, "Designation Specific")

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

        # dropbox
        self._dropdown_label = QLabel("Select Designation")
        self.dropdown = QComboBox()
        designations = ["Admin", "HR", "Intern", "Ops AE", "Ops PE/ TL", "Ops SE", "Ops- Regional Leads", "missing",
                        "BD-Head", "Ops- Head- Utilities", "Ops Head- Economics",
                        "Ops Head- Power Sys Studies & Equipment Modelling", "Ops- Global Head"]
        for designation in designations:
            self.dropdown.addItem(designation)
        # TODO : This should take a list od designations of the various employees you can also take it according to the different designations that are present dynamically

        self.plot_button = QPushButton("Analyze")
        self.plot_button.clicked.connect(self.update_graphs_and_tables)

        # layout for section 2
        self._section2_layout = QVBoxLayout()
        self._section2_layout.addWidget(self._dropdown_label)
        self._section2_layout.addWidget(self.dropdown)
        self._section2_layout.addWidget(self.plot_button)
        self._section2_layout.addWidget(self.plot_button)
        self._section2_layout.addWidget(self.main_tab_widget)

        section2_container = QWidget()
        section2_container.setLayout(self._section2_layout)

        # layout for whole window
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._designation_table)
        main_layout.addWidget(section2_container)

        self.setLayout(main_layout)

    def update_graphs_and_tables(self):
        designation = self.dropdown.currentText()
        self.side_table_widget.clear()
        designation_data = self._df[self._df['Category'] == designation]
        rows = self._grouped_df[self._grouped_df['Category'] == designation]
        write_df_to_table(self, rows, self.side_table_widget)
        for i in reversed(range(self.graph_widget1_layout.count())):
            self.graph_widget1_layout.itemAt(i).widget().deleteLater()
            self.graph_widget2_layout.itemAt(i).widget().deleteLater()
            self.graph_widget3_layout.itemAt(i).widget().deleteLater()
        query1 = designation_data.groupby('Work Items')['Duration'].sum()
        pie_widget1 = create_pie_chart_widget(query1, query1.index, title='Work Items Distribution for {}'.format(designation))
        self.graph_widget1_layout.addWidget(pie_widget1)

        query2 = designation_data.groupby('Product_Service')['Duration'].sum()
        pie_widget2 = create_pie_chart_widget(query2, query2.index,
                                              title='Product/Service Distribution for {}'.format(designation))
        self.graph_widget2_layout.addWidget(pie_widget2)

        query3 = designation_data.groupby('Billable')['Duration'].sum()
        pie_widget3 = create_pie_chart_widget(query3, query3.index,
                                              title='Billability for {}'.format(designation))
        self.graph_widget3_layout.addWidget(pie_widget3)
        # pass

    def _reset_designation_table(self):
        self._designation_table.clear()
        self._designation_table.setRowCount(0)

    @property
    def designation_table(self):
        return self._designation_table
