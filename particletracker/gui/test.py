import sys
from PyQt6.QtCore import QObject, pyqtSignal, QModelIndex, Qt
from PyQt6.QtWidgets import QApplication

# A simple class that will act as the signal emitter
class Emitter(QObject):
    test_signal = pyqtSignal(QModelIndex, QModelIndex, list)

# A simple class that has the debugging slot
class Receiver(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    # Use *args to receive all arguments from the signal
    def debug_slot(self, *args):
        print("Debug Slot Fired!")
        print("Received arguments:")
        for i, arg in enumerate(args):
            print(f"  Argument {i}: Type = {type(arg)}, Value = {arg}")
        print("-" * 20)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    emitter = Emitter()
    receiver = Receiver()
    
    # Connect the signal to the generic debugging slot
    emitter.test_signal.connect(receiver.debug_slot)

    # Create dummy data to emit with the signal
    dummy_index1 = QModelIndex()
    dummy_index2 = QModelIndex()
    dummy_list = [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole]
    
    # Emit the signal with the dummy data
    emitter.test_signal.emit(dummy_index1, dummy_index2, dummy_list)

    # The output will show the types of the arguments received by debug_slot
    # Output:
    # Debug Slot Fired!
    # Received arguments:
    #  Argument 0: Type = <class 'PyQt6.QtCore.QModelIndex'>, Value = <PyQt6.QtCore.QModelIndex object at ...>
    #  Argument 1: Type = <class 'PyQt6.QtCore.QModelIndex'>, Value = <PyQt6.QtCore.QModelIndex object at ...>
    #  Argument 2: Type = <class 'list'>, Value = [<ItemDataRole.DisplayRole: 0>, <ItemDataRole.EditRole: 2>]
    # --------------------

    sys.exit(app.exec())