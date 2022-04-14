import os

import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt

from ..customexceptions import PandasViewError


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
        self.parent = parent
        self.view = QtWidgets.QTableView()
        model = pandasModel(pd.DataFrame())
        self.view.setModel(model)
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
        w = int(self.parent.screen_size.width() / 2)
        h = int(self.parent.screen_size.height() / 1.5)
        self.resize(w, h)
        self.move(int(0.975*w),int(h/5))
        

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.parent.pandas_button.setChecked(False)
        return super().closeEvent(a0)
    
    def close_button_clicked(self):
        self.hide()
        self.parent.pandas_button.setChecked(False)
        

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

    def update_file(self, filename, frame):
        self.filename = filename
        try:
            df = pd.read_hdf(filename)            
            if 'frame' in df.columns:
                df2 = df[df.index == frame]    
            else:
                df2 = df.reset_index()
        except Exception as e:
            self.df = pd.DataFrame()
            raise PandasViewError(e)
        self.df=df2
        model = pandasModel(df2)
        self.view.setModel(model)

