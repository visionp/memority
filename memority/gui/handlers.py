import asyncio
from threading import Event

from PyQt5.QtCore import QThread
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from dialogs import ask_for_password


def rm_last_line(log_widget):
    cursor = log_widget.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.select(QTextCursor.LineUnderCursor)
    cursor.removeSelectedText()
    cursor.deleteChar()
    log_widget.moveCursor(QTextCursor.End)


class PreloaderThread(QThread):
    def __init__(self, log_widget):
        super().__init__()
        self.log_widget = log_widget
        self.stop_event = Event()

    def run(self):
        i, d = 0, 0
        toolbar_width = 50
        tw = toolbar_width - 4
        while not self.stop_event.is_set():
            w1 = i % tw
            if w1 == 0:
                d += 1
                if i != 0:
                    i += 1
                    continue
            w2 = tw - w1 - 1
            s = f'{" " * w1}...{" " * w2}'
            rm_last_line(self.log_widget)
            # ToDo: can not interact with widget from thread. Use signal-slot
            self.log_widget.appendPlainText(s if d % 2 else ''.join(reversed(s)))
            self.log_widget.moveCursor(QTextCursor.End)
            i += 1
            self.stop_event.wait(0.2)


def log(msg, log_widget: QPlainTextEdit, preloader=False):
    # global preloader_thread
    # if preloader_thread:
    #     preloader_thread.stop_event.set()
    #     preloader_thread.join()
    #     preloader_thread = None
    #     rm_last_line(log_widget)

    log_widget.appendPlainText(msg)
    log_widget.moveCursor(QTextCursor.End)
    # if preloader:
    #     preloader_thread = PreloaderThread(log_widget)
    #     preloader_thread.start()


def uploaded_file_handler(data, window):
    file_data = data.get('data').get('file')
    window.add_file_list_item(**file_data)
    log(f'Your file successfully uploaded! Hash: {file_data.get("hash")}', window.log_widget)


def downloaded_file_handler(data, window):
    file_data = data.get('data').get('file')
    log(f'Your file successfully downloaded! Path: {file_data.get("name")}', window.log_widget)


def file_list_handler(data, window):
    file_list = data.get('data').get('files')
    window.cleanup_file_list()
    for file in file_list:
        window.add_file_list_item(**file)


def error_handler(message_data, window=None):
    message = message_data.get('message') if isinstance(message_data, dict) else message_data
    if 'insufficient funds' in message:
        message = 'Error\n' \
                  'Account cannot be created without MMR tokens.\n' \
                  'Please send your generated address to info@memority.io to receive tokens.'
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText("Error")
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.exec()


def action_handler(message_data, window):
    action = message_data.get('details')
    if action == 'ask_for_password':
        password, ok = ask_for_password(message_data.get('message'))
        asyncio.ensure_future(window.ws_send({"status": "success", "password": password}))
    else:
        message = message_data.get('message')
        type_ = message_data.get('type')
        if type_ == 'bool':
            reply = QMessageBox().question(
                None,
                message,
                message,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            result = True if reply == QMessageBox.Yes else False
        elif type_ == 'float':
            inputDialog = QInputDialog(None)
            inputDialog.setInputMode(QInputDialog.DoubleInput)
            inputDialog.setWindowTitle(message)
            inputDialog.setLabelText(message)
            inputDialog.setDoubleValue(1)
            inputDialog.exec_()
            result = inputDialog.doubleValue()
        else:
            inputDialog = QInputDialog(None)
            inputDialog.setInputMode(QInputDialog.TextInput)
            inputDialog.setWindowTitle(message)
            inputDialog.setLabelText(message)
            inputDialog.setFixedSize(400, 100)
            inputDialog.exec_()
            result = inputDialog.textValue()
        asyncio.ensure_future(window.ws_send({'status': 'success', 'result': result}))


def info_handler(message_data, window):
    log(
        message_data.get('message'),
        window.log_widget,
        preloader=message_data.get('preloader', False)
    )


WS_MESSAGE_HANDLERS = {
    "uploaded": uploaded_file_handler,
    "downloaded": downloaded_file_handler,
    "file_list": file_list_handler,
    "info": info_handler,
}


def process_ws_message(message_data: dict, window):
    status = message_data.get('status')
    if status == 'success':
        handler = WS_MESSAGE_HANDLERS.get(message_data.get('details'))
    elif status == 'action_needed':
        handler = action_handler
    else:
        handler = error_handler
    if handler:
        return handler(message_data, window)
