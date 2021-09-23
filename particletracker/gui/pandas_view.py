import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ..customexceptions import PandasViewError

import os

class pandasModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

class PandasWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.view = QtWidgets.QTableView()
        model = pandasModel(pd.DataFrame())
        self.view.setModel(model)
        self.view.resize(800, 600)
        self.view.show()
        self.view.setModel(model)
        self.view.resize(800, 600)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.view)
        button_layout = QtWidgets.QHBoxLayout()
        close_button = QtWidgets.QPushButton("Close", self)
        save_to_csv_button = QtWidgets.QPushButton("Save", self)
        button_layout.addWidget(close_button)
        button_layout.addWidget(save_to_csv_button)
        close_button.clicked.connect(self.close_button_clicked)
        save_to_csv_button.clicked.connect(self.save_button_clicked)

        lay.addLayout(button_layout)
        self.setLayout(lay)
        self.view.show()
        self.setWindowTitle('df')
        self.resize(800, 600)
        self.center()

    def close_button_clicked(self):
        self.hide()

    def save_button_clicked(self):
        options = QtWidgets.QFileDialog.Options()
        directory = os.path.split(self.filename)[0]
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save to csv", directory, "csv (*.csv)")
        name = name.split('.')[0]+'.csv'
        self.df.to_csv(name)

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_file(self, filename):
        self.filename = filename
        try:
            df = pd.read_hdf(filename).reset_index()
        except Exception as e:
            df = pd.DataFrame()
            raise PandasViewError(e)
        self.df = df
        model = pandasModel(df)
        self.view.setModel(model)

