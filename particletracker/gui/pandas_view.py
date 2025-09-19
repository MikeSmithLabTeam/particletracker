import os

import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt

from ..customexceptions import *


class pandasModel_read(QtCore.QAbstractTableModel):

    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None


class pandasModel_edit(QtCore.QAbstractTableModel):

    def __init__(self, data):
        QtCore.QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            if value == str(0): #deal with zero error
                value = np.float(0)
            self._data.iloc[index.row(), index.column()] = np.float64(value) #set new values

            return True
        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None
    
    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    

class PandasWidget(QtWidgets.QDialog):
    def __init__(self, parent=None, edit=False):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.edit = edit #set edit flag i.e edit or read-only.


        if self.edit == False:    #read only dataframe viewer
            self.view = QtWidgets.QTableView()
            model = pandasModel_read(pd.DataFrame())
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


        if self.edit == True:    #editable dataframe viewer
            self.view = QtWidgets.QTableView()
            model = pandasModel_edit(pd.DataFrame())
            self.view.setModel(model)
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.view)
            button_layout = QtWidgets.QHBoxLayout()
            
            add_row_button = QtWidgets.QPushButton("Add row", self)
            delete_row_button = QtWidgets.QPushButton("Delete row", self)
            save_button = QtWidgets.QPushButton("Save", self)
            reset_button = QtWidgets.QPushButton("Reset", self)
            
            button_layout.addWidget(add_row_button)
            button_layout.addWidget(delete_row_button)
            button_layout.addWidget(save_button)
            button_layout.addWidget(reset_button)

            add_row_button.clicked.connect(self.add_row_clicked)
            delete_row_button.clicked.connect(self.delete_row_clicked)
            save_button.clicked.connect(self.save_button_clicked)
            reset_button.clicked.connect(self.reset_button_clicked)
        


        lay.addLayout(button_layout)
        self.setLayout(lay)
        self.view.show()
        self.setWindowTitle('df')

        # Get screen size using QScreen
        screen = self.screen()
        if screen:
            screen_size = screen.size()
            w = int(screen_size.width() / 2)
            h = int(screen_size.height() / 1.5)
            self.resize(w, h)
            self.move(int(0.975*w), int(h/5))
    
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.parent.pandas_button.setChecked(False)
        return super().closeEvent(a0)
    
    def close_button_clicked(self):
        self.hide()
        self.parent.pandas_button.setChecked(False)
        
    def save_button_clicked(self):
        directory = os.path.split(self.filename)[0]
        name, _ = QtWidgets.QFileDialog.getSaveFileName(
        self, 
        "Save to csv", 
        directory, 
        "csv (*.csv)", 
        options=QtWidgets.QFileDialog.Option.DontUseNativeDialog)
        name = name.split('.')[0]+'.csv'
        self.df.to_csv(name)
    
    def message_box(self, msg_string):
        """
        Displays message pop up. Takes message string to be displayed as input.
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setText(str(msg_string))
        msg.show()

    def add_row_clicked(self):
        """
        Adds row to existing dataframe. Function adds a copy of the row selected by the user into the 
        dataframe. New row is inserted below the selected row. Once row is inserted, the pandasModel is
        updated and changes are displayed in GUI. Displays message if no row is selected.
        """

        index = self.view.currentIndex()
        row_idx = index.row()
        if row_idx == -1:
            msg = "No row selected."
            self.message_box(msg)
        else:
            new_item = pd.DataFrame(self.df.iloc[[row_idx]])
            self.df = pd.concat([self.df, new_item], ignore_index=True).sort_values("particle")
            model = pandasModel_edit(self.df)
            self.view.setModel(model)
            self.view.selectRow(row_idx)
            self.write_to_file()

    def delete_row_clicked(self):
        """
        Deletes row in dataframe selected by the user. Function extracts selected row index, drops row 
        from the dataframe, updates the pandasModel and displays changes in the GUI. Displays message if 
        no row has been selected.
        """
        index = self.view.currentIndex() 
        row_idx = index.row()
        
        if row_idx == -1:
            msg = "No row selected"
            self.message_box(msg)
        else:
            self.df = self.df.drop([row_idx])
            self.df = self.df.reset_index(drop=True)
            model = pandasModel_edit(self.df)
            self.view.setModel(model)
            self.write_to_file()
    
    def reset_button_clicked(self):
        """
        Reverts changes made to the dataframe. Loads a copy of the original dataframe loaded 
        by the user.
        """
        self.update_file_editable("data_temp.hdf5", 1)
        self.message_box("Changes reverted")

    def write_to_file(self):
        """
        Writes dataframe displayed in the window to a .hdf5 file
        """
        try:
            self.df.to_hdf(".hdf5", key="data", mode="w")
        except Exception as e:
            self.df = pd.DataFrame()
            raise PandasViewError(e)

    def update_file(self, filename, frame):
        self.filename = filename

        try:
            df = pd.read_hdf(filename)
            if "frame" in df.columns:
                df2 = df[df.index == frame]
            else:
                df2 = df.reset_index()
        except Exception as e:
            self.df = pd.DataFrame()
            raise PandasViewError(e)
        
        self.df = df2
        model = pandasModel_read(df2)
        self.view.setModel(model)

    def update_file_editable(self, filename, frame):
        """
        Reads in dataframe from .hdf5 file and sorts dataframe based on particle number.
        Saves copy of the dataframe as a temp .hdf5 file. Selects section of dataframe
        corresponding to selected frame number. Then sets the model to be used by the
        QAbstractTabelModel() class in the GUI window.
        """

        self.filename = filename
        
        try: 
            df = pd.read_hdf(filename).sort_values("particle")

            if os.path.exists("data_temp.hdf5") == False:
                df.to_hdf("data_temp.hdf5", key="data", mode="w")
            if "frame" in df.columns:
                df2 = df[df["frame"] == frame]
            else:
                df2 = df
        except Exception as e:
            self.df = pd.DataFrame()
            raise PandasViewError(e)

        self.df = df2
        model = pandasModel_edit(df2)
        self.view.setModel(model)


