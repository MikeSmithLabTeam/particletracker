import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

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
    def __init__(self, df_filename='', frame_number=0, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        df = pd.read_hdf(df_filename).loc[frame_number].reset_index()
        model = pandasModel(df)
        view = QtWidgets.QTableView()
        view.setModel(model)
        view.resize(800, 600)
        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(view)
        self.setLayout(lay)
        view.show()
        self.setWindowTitle('df')
        self.resize(800, 600)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

