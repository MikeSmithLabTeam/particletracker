import os

import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from ..general.dataframes import DataRead, combine_data_frames
from ..customexceptions import *
from ..gui.menubar import CustomButton

class pandasModel(QtCore.QAbstractTableModel):

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

    def headerData(self, col, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        return None
    
class pandasModel_edit(pandasModel):
    data_change = pyqtSignal()

    def __init__(self, data):
        super(pandasModel_edit,self).__init__(data)
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def insertDataRow(self, row_idx, data_row):
        """Inserts a DataFrame row at row_idx using PyQt model mechanisms."""
        self.beginInsertRows(QtCore.QModelIndex(), row_idx, row_idx)
        df_top = self._data.iloc[:row_idx]
        df_bottom = self._data.iloc[row_idx:]
        
        if isinstance(data_row, pd.Series):
             new_row_df = pd.DataFrame([data_row], columns=self._data.columns)
        else: 
             new_row_df = data_row
        self._data = pd.concat([df_top, new_row_df, df_bottom], ignore_index=True)
        self.endInsertRows()
        return True
    
    def removeDataRow(self, row_idx,):
        """Removes a DataFrame row at row_idx using PyQt model mechanisms."""
        self.beginInsertRows(QtCore.QModelIndex(), row_idx, row_idx)
        df_top = self._data.iloc[:row_idx]
        if row_idx == len(self._data)-1:
            self._data = df_top
        else:
            df_bottom = self._data.iloc[row_idx+1:]
            self._data = pd.concat([df_top, df_bottom], ignore_index=True)
        self.endInsertRows()
        return True
        

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            if value == str(0):
                value = np.float64(0)
            
            try:
                self._data.iloc[index.row(), index.column()] = np.float64(value)
            except ValueError:
                return False

            self.data_change.emit()
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    

class PandasWidget(QtWidgets.QDialog):
    # Declare the custom signal
    data_updated_signal = pyqtSignal(int, DataRead)
        
    def __init__(self, parent=None, edit=False, data=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.edit = edit #set edit flag i.e edit or read-only.
        self.data = data    
        self.f_index = None

        if self.edit:    #editable dataframe viewer
            self.view = QtWidgets.QTableView()
            self.model = pandasModel_edit(pd.DataFrame())
            self.view.setModel(self.model)
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.view)
            button_layout = QtWidgets.QHBoxLayout()
            self.model.data_change.connect(self._data_update)
            
            add_row_button = QtWidgets.QPushButton("Add row", self)
            delete_row_button = QtWidgets.QPushButton("Delete row", self)
            save_button = QtWidgets.QPushButton("Save", self)
            reset_button = QtWidgets.QPushButton("Reset", self)
            
            button_layout.addWidget(add_row_button)
            button_layout.addWidget(delete_row_button)
            button_layout.addWidget(save_button)
            button_layout.addWidget(reset_button)

            add_row_button.clicked.connect(self.add_row_clicked)
            delete_row_button.clicked.connect(self.remove_row_clicked)
            save_button.clicked.connect(lambda x : self._data_update(write=True))
            reset_button.clicked.connect(self.reset_button_clicked)
        
        else:    #read only dataframe viewer
            self.view = QtWidgets.QTableView()
            self.model = pandasModel(pd.DataFrame())
            self.view.setModel(self.model)
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
        
        self.title = None

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
        return super().closeEvent(a0)
    
    def close_button_clicked(self):
        self.hide()

    def save_button_clicked(self):
        directory = os.path.split(self.data.temp_filename)[0][:-6]
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
        Adds a copy of the selected row immediately below the selected row 
        in the underlying DataFrame, then updates the QTable and saves the state.
        """
        lock_part = CustomButton.locked_part
        store = self.data._stores[lock_part]

        index = self.view.currentIndex()
        row_idx = index.row()
       
        selected_row_data = self.model._data.iloc[row_idx] 

        new_row_idx = row_idx + 1
        self.model.insertDataRow(new_row_idx, selected_row_data)


        if 'particle' in self.model._data.columns:
            max_particle_id = self.model._data['particle'].max()
            new_particle_id = int(max_particle_id) + 1
            
            particle_col_loc = self.model._data.columns.get_loc('particle')
            self.model._data.iloc[new_row_idx, particle_col_loc] = new_particle_id

        new_index = self.model.index(new_row_idx, 0)
        self.view.setCurrentIndex(new_index)
        self.view.selectRow(new_row_idx)
        
        self._data_update()

    def remove_row_clicked(self):
        """
        Removes the currently selected row from the underlying DataFrame, 
        updates the QTable, and saves the state.
        """
        lock_part = CustomButton.locked_part
        store = self.data._stores[lock_part]

        index = self.view.currentIndex()
        row_idx = index.row()
        self.model.removeDataRow(row_idx)        
        self._data_update()
            
    def reset_button_clicked(self):
        """
        Reverts changes made to the dataframe. Loads a copy of the original dataframe loaded 
        by the user.
        """
        store = self.data._stores[CustomButton.locked_part]
        store.clear_df()
        self.data_updated_signal.emit(self.f_index, store)
        self.message_box("Changes reverted")

    def _data_update(self, write=False):
        """
        Stores changes to the DataRead store. These changes are reversible.
        """
        lock_index = CustomButton.locked_part   
        store = self.data._stores[lock_index]
        self.model._data.set_index(np.ones(self.model._data.shape[0]) * self.f_index, inplace=True)
        self.model._data.index.name = 'frame'

        
        store._df.drop(index=self.f_index, inplace=True)
        store._df = pd.concat([self.model._data, store._df], sort=True)


        if write:
            store._df.to_hdf(store.read_filename, key="data")

        self.data_updated_signal.emit(lock_index, store)

    def update_file(self, f_index):
        try:
            self.f_index=f_index
            store = self.data.post_store
            store.clear_temp_df()
            temp_df = store.temp_df
            title = f'Reading frame : '
            self.setWindowTitle(title + str(f_index))
        except Exception as e:
            temp_df = pd.DataFrame()
            raise PandasViewError(e)
        
        temp_df = order_headings(temp_df)
        self.model = pandasModel(temp_df)
        self.view.setModel(self.model)

    def update_file_editable(self, f_index):
        """
        Updates the model's data to a new DataFrame.
        """
        self.model.beginResetModel()

        self.f_index = f_index
        lock_index = CustomButton.locked_part
        if lock_index == -1:
            df_frame = pd.DataFrame()
        else:
            store = self.data._stores[lock_index]
            df_frame = store.get_df(f_index=f_index)
            if 'particle' not in df_frame.columns or (  'particle' in df_frame.columns and df_frame['particle'].isnull().all()
):
                num_particles = np.shape(df_frame)[0]
                df_frame['particle'] = np.linspace(0, num_particles - 1, num=num_particles).astype(int)
        df_frame = order_headings(df_frame)
        
        self.model._data = df_frame

        if CustomButton.locked_part == 0:
            title = f'Editing tracking frame : '
        elif CustomButton.locked_part == 1:
            title = f'Editing linking frame : '
        elif CustomButton.locked_part == 2:
            title = f'Editing postprocessing frame : '
        else:
            title = f'Can only edit with a stage locked'
        self.setWindowTitle(title + str(f_index))

        self.model.endResetModel()

    
def order_headings(df):
    # Define a list of columns that should always appear first (lowercase for comparison)
    fixed_order_names = ['particle', 'x', 'y']
    column_map = {col.strip().lower(): col for col in df.columns}
    
    desired_order_original_case = []
    
    for target_name in fixed_order_names:
        original_name = column_map.get(target_name)
        if original_name is not None:
            desired_order_original_case.append(original_name)
    other_columns_original_case = []
    
    for col in sorted(df.columns):
        if col.strip().lower() not in fixed_order_names:
            other_columns_original_case.append(col)
    
    final_order = desired_order_original_case + other_columns_original_case
    
    return df.reindex(columns=final_order, fill_value=np.nan)


