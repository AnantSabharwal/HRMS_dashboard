import os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QTableWidgetItem, \
    QPushButton

from general.general_functions import write_df_to_table


class ServicePanelWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Analysis Based on Location")
        font = QFont()
        font.setBold(True)
        #internal df
        self._grouped_df = None
        # Layout for section 1 (Left Side)
        self._service_table = QTableWidget()
        self._service_table.setSortingEnabled(True)
        self._service_table_label = QLabel("Service")
        self._reset_service_table()

        # Layout for section 2 (Right Side)
        self.side_table_widget = QTableWidget()
        self.side_table_widget.setSortingEnabled(True)

        # Dropdown for selecting name
        self.dropdown_label = QLabel("Select Name")
        self.dropdown = QComboBox()
        # dropdown.currentIndexChanged.connect(self.update_table)

        self.plot_button = QPushButton("Analyze")
        self.plot_button.clicked.connect(self.update_table)

        _section2_layout = QVBoxLayout()
        _section2_layout.addWidget(self.dropdown_label)
        _section2_layout.addWidget(self.dropdown)
        _section2_layout.addWidget(self.plot_button)
        _section2_layout.addWidget(self.side_table_widget)

        # Layout for whole window
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._service_table)
        main_layout.addLayout(_section2_layout)

        self.setLayout(main_layout)

    def update_table(self):
        service_name = self.dropdown.currentText()
        self.side_table_widget.clear()
        rows = self._grouped_df[self._grouped_df['Product_Service'] == service_name]
        write_df_to_table(self, rows, self.side_table_widget)
        # pass

    def _reset_service_table(self):
        self._service_table.clear()
        self._service_table.setRowCount(0)

    @property
    def service_table(self):
        return self._service_table