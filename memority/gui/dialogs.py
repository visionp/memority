from PyQt5.QtWidgets import *

__all__ = ['ask_for_password', 'ask_for_int']


def ask_for_password(msg):
    inputDialog = QInputDialog(None)
    inputDialog.setInputMode(QInputDialog.TextInput)
    inputDialog.setTextEchoMode(QLineEdit.Password)
    inputDialog.setLabelText(msg)
    inputDialog.setFixedSize(400, 100)
    ok = inputDialog.exec_()
    text = inputDialog.textValue()
    return text, ok


def ask_for_int(message, default=None, maximum=None):
    dialog = QInputDialog(None)
    dialog.setInputMode(QInputDialog.IntInput)
    if maximum:
        dialog.setIntMaximum(maximum)
    dialog.setLabelText(message)
    if default:
        dialog.setIntValue(default)
    dialog.setFixedSize(400, 100)
    status = dialog.exec_()
    result = dialog.intValue()
    return result, status
