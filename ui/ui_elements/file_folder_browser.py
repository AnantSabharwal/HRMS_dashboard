import logging
import os
import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QToolBar, QLineEdit, QAction, QTreeView, QSizePolicy, \
    QFileSystemModel, QFileDialog


class FileFolderBrowser(QWidget):
    fetchresult = pyqtSignal(str)

    def __init__(self, parent=None, message="", icons="", init_path='', file_filter=None,
                 file_browser=True, placeholder_text="", add_clear_button=False,
                 show_tree_view=True):
        super(FileFolderBrowser, self).__init__(parent)

        if file_filter is None:
            file_filter = '*.*'
        self._logger = logging.getLogger(__name__)
        self._placeholder_text = placeholder_text
        self._message = message
        self._layout = QVBoxLayout()
        self._file_browser = file_browser
        self._show_tree_view = show_tree_view
        self._add_clear_button = add_clear_button
        if init_path == '' or None:
            self._path = ''
        else:
            self._path = init_path
        self._file_filter = file_filter
        self._icons = icons
        self._tb = self._add_toolbar()
        self._add_treeview()

        self._layout.addWidget(self._tb)
        if self._show_tree_view:
            self._layout.addWidget(self._treeview)

        self._treeview.setFocus()
        self.setLayout(self._layout)

    def _add_toolbar(self):
        toolbar = QToolBar()
        self._pathwidget = QLineEdit()
        if self._path:
            self._pathwidget.setText(self._path)
        self._pathwidget.setPlaceholderText(self._placeholder_text)
        toolbar.addWidget(self._pathwidget)
        self._pathwidget.setReadOnly(True)

        browse_btn = QAction(QIcon(os.path.join(self._icons, "browse.png")), "Browse", self)
        toolbar.addAction(browse_btn)
        browse_btn.triggered.connect(self.browse)
        if self._add_clear_button:
            clear_button = QAction(QIcon(os.path.join(self._icons, "remove_item.png")), "Clear", self)
            toolbar.addAction(clear_button)
            clear_button.triggered.connect(self._clear_path)
        return toolbar

    def _add_treeview(self):
        self._treeview = QTreeView()
        self._treeview.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self._dir_model = QFileSystemModel()
        self._treeview.setModel(self._dir_model)

        # add filename filter
        self._dir_model.setNameFilters([self._file_filter])
        self._dir_model.setNameFilterDisables(0)
        self._update_treeview(self.path)

        self._treeview.hideColumn(1)
        self._treeview.hideColumn(2)
        self._treeview.hideColumn(3)

    def _update_treeview(self, path):
        if path:
            if os.path.isdir(path):
                self._dir_model.setRootPath(path)
                self._treeview.setRootIndex(self._dir_model.index(path))
            else:
                self._dir_model.setRootPath(os.path.dirname(path))
                self._treeview.setRootIndex(self._dir_model.index(os.path.dirname(path)))

            self._treeview.setCurrentIndex(self._dir_model.index(path))
            self._treeview.setAlternatingRowColors(True)
            self._treeview.resizeColumnToContents(0)

    @property
    def path(self):
        if self._path is None:
            return ""
        else:
            return self._path

    @path.setter
    def path(self, path):
        if path:
            self._path = str(path)
            self._logger.debug("Path assigned to {}".format(self.path))

    def browse(self):
        if self._file_browser:
            path = QFileDialog.getOpenFileName(self, self._message, self.path, filter=self._file_filter)
            if isinstance(path, tuple):
                path = path[0]
            self.path = str(path)
            self._update_path()
        else:
            path = QFileDialog.getExistingDirectory(self, self._message)
            self.path = str(path)
            self._update_path()

    def _update_path(self):
        if self.path:

            self._pathwidget.setText(self.path)
            self._update_treeview(self.path)
            self.fetchresult.emit(self.path)

    def set_path(self, path):
        if os.path.exists(path):
            self.path = path
            self._update_path()
            if not os.path.isdir(self.path) and not self._file_browser:
                self._update_treeview(os.path.dirname(self.path))
                self._treeview.setFocus()
            return True
        else:
            return False

    def _clear_path(self):
        # this is forced clearing of path required in certain cases
        self._path = None
        self._pathwidget.setText('')
        self._update_treeview('')
        self.fetchresult.emit("")



