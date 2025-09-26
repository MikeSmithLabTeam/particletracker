import os

import pandas as pd
import numpy as np
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot


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
    def __init__(self, data):
        super(pandasModel_edit,self).__init__(data)
        
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def setData(self, index, value, role):
        print('setData', index, value, role)
        if role == Qt.ItemDataRole.EditRole:
            if value == str(0):
                value = np.float64(0)
            
            try:
                self._data.iloc[index.row(), index.column()] = np.float64(value)
            except ValueError:
                # Return False if the conversion failed
                return False

            # Just can't get this to connect
            #self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    

class PandasWidget(QtWidgets.QDialog):
    # Declare the custom signal
    data_updated_signal = pyqtSignal()
        
    def __init__(self, parent=None, edit=False, data=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.edit = edit #set edit flag i.e edit or read-only.
        self.data = data    
        self.frame = None

        if self.edit:    #editable dataframe viewer
            self.view = QtWidgets.QTableView()
            self.model = pandasModel_edit(pd.DataFrame())
            self.view.setModel(self.model)
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.view)
            button_layout = QtWidgets.QHBoxLayout()
            
            update_button = QtWidgets.QPushButton("Update", self)
            add_row_button = QtWidgets.QPushButton("Add row", self)
            delete_row_button = QtWidgets.QPushButton("Delete row", self)
            save_button = QtWidgets.QPushButton("Save", self)
            reset_button = QtWidgets.QPushButton("Reset", self)
            
            button_layout.addWidget(update_button)
            button_layout.addWidget(add_row_button)
            button_layout.addWidget(delete_row_button)
            button_layout.addWidget(save_button)
            button_layout.addWidget(reset_button)

            update_button.clicked.connect(self.update_clicked)
            add_row_button.clicked.connect(self.add_row_clicked)
            delete_row_button.clicked.connect(self.delete_row_clicked)
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
        self.setWindowTitle(f'df - frame')

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

    def update_clicked(self):
        self._data_update()

    def add_row_clicked(self):
        """
        Adds row to existing dataframe. Function adds a copy of the row selected by the user into the 
        dataframe. New row is inserted below the selected row. Once row is inserted, the pandasModel is
        updated and changes are displayed in GUI. Displays message if no row is selected.
        """
        lock_index = CustomButton.locked_part   
        store = self.data._stores[lock_index]

        if store._df is None:
            store.df

        index = self.view.currentIndex()
        row_idx = index.row()

        if row_idx == -1:
            msg = "No row selected."
            self.message_box(msg)
        else:
            new_item = pd.DataFrame(self.df.iloc[[row_idx]])
            self.df = pd.concat([self.df, new_item], ignore_index=True).sort_values("particle")

        self.model = pandasModel_edit(self.df)
        self.view.setModel(self.model)
        self.view.selectRow(row_idx)
        self._data_update()

    def delete_row_clicked(self):
        """
        Deletes row in dataframe selected by the user. Function extracts selected row index, drops row 
        from the dataframe, updates the pandasModel and displays changes in the GUI. Displays message if 
        no row has been selected.
        """
        lock_index = CustomButton.locked_part   
        store = self.data._stores[lock_index]

        if store._df is None:
            store.df

        index = self.view.currentIndex() 
        row_idx = index.row()
        
        if row_idx == -1:
            msg = "No row selected"
            self.message_box(msg)
        else:
            drop_label = self.df.iloc[row_idx]["particle"]
            self.df = self.df.set_index("particle")
            self.df = self.df.drop([drop_label]).sort_values("particle")
            self.df = self.df.reset_index()
            self.model = pandasModel_edit(self.df)
            self.view.setModel(self.model)
        self._data_update()      
        

    def reset_button_clicked(self):
        """
        Reverts changes made to the dataframe. Loads a copy of the original dataframe loaded 
        by the user.
        """
        self.data._stores[CustomButton.locked_part].clear_data()
        self.update_file_editable(self.frame)
        self.message_box("Changes reverted")
        self._data_update()

    def _data_update(self, write=False):
        """
        Stores changes to the DataRead store. These changes are reversible.
        """
        lock_index = CustomButton.locked_part   
        store = self.data._stores[lock_index]
               
        self.df.set_index(np.ones(self.df.shape[0]) * self.frame, inplace=True)
        self.df.index.name = 'frame'

        _original = store.full
        store.full=True

        if store._df is None:
            store.df
        store._df.drop(index=self.frame, inplace=True)
        store._df = pd.concat([self.df, store._df], sort=True)
        print('Storing data')
        print(self.df)
        print(store._df)
    
        if write:
            store._df.to_hdf(store.read_filename, key="data")
        store.full=_original
        self.data_updated_signal.emit()

    def update_file(self, frame):
        try:
            self.frame=frame
            store = self.data.post_store
            _original = store.full
            store.full=False
            df2 = store.get_df(f_index=frame)
            self.data.post_store.full=_original
            self.df=df2
            #self.setWindowTitle(f'df - frame = {frame}')
        except Exception as e:
            self.df = pd.DataFrame()
            raise PandasViewError(e)
        
        df2 = order_headings(df2)
        self.model = pandasModel(self.df)
        self.view.setModel(self.model)

    def update_file_editable(self, frame):
        """
        Updates the model's data to a new DataFrame.
        """
        # 1. Start the model reset process. This tells the view to stop listening for data changes.
        self.model.beginResetModel()

        # 2. Update the underlying data.
        self.frame = frame
        lock_index = CustomButton.locked_part
        if lock_index == -1:
            df2 = pd.DataFrame()
        else:
            store = self.data._stores[lock_index]
            df2 = store.get_df(f_index=frame)
            if 'particle' not in df2.columns:
                num_particles = np.shape(df2)[0]
                df2['particle'] = np.linspace(0, num_particles - 1, num=num_particles).astype(int)

        df2 = order_headings(df2)
        # The crucial line: Update the model's internal data.
        self.model._data = df2
        self.df = df2
        
        # 3. End the model reset process. This tells the view to reread all data from the model.
        self.model.endResetModel()

        # You can now emit your custom signal to notify other parts of the GUI
        #self.data_updated_signal.emit()
    
    '''def update_file_editable(self, frame):
        """
        Selects section of dataframe
        corresponding to selected frame number. Then sets the model to be used by the
        QAbstractTabelModel() class in the GUI window.
        """
        self.frame = frame        
        lock_index = CustomButton.locked_part
        if lock_index == -1:
            df2=pd.DataFrame()
        else:
            store = self.data._stores[lock_index]
            _original = store.full
            print('store df', store._df)
            store.full=True
            df2 = store.get_df(f_index=frame)
            store.full=_original
            print('update_editable', df2)
            if 'particle' not in df2.columns:
                num_particles = np.shape(df2)[0]
                df2['particle']=np.linspace(0,num_particles-1, num=num_particles).astype(int)
        
        df2 = order_headings(df2)
        self.df = df2
        print('b4 model', df2)
        self.model = pandasModel_edit(df2)
        self.view.setModel(self.model)
        print('finished')'''

def order_headings(df):
    # Define a list of columns that should always appear first
    fixed_order = ['particle', 'x', 'y']
    
    # Get all other columns and sort them alphabetically
    other_columns = sorted([col for col in df.columns if col not in fixed_order])
    
    # Combine the fixed order with the other columns to create the final, consistent order
    desired_order = fixed_order + other_columns
    
    # Re-index the DataFrame to enforce the desired order
    return df.reindex(columns=desired_order, fill_value=np.nan)


