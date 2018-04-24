#! /usr/bin/env python

import asyncio
import contextlib
import json
import sys
from asyncio import CancelledError

import aiohttp
import requests
from PyQt5.QtWidgets import *
from quamash import QEventLoop

from bugtracking import raven_client
from dialogs import ask_for_password
from handlers import process_ws_message, error_handler
from settings import settings
from tabs import TabsWidget


class MainWindow(QMainWindow):

    def __init__(self, event_loop: QEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ws = None
        self.session = aiohttp.ClientSession()
        self.event_loop = event_loop
        self.resize(1024, 600)
        self.setWindowTitle('Memority GUI')

        container = QWidget(self)
        self.setCentralWidget(container)

        self.msg_for_testers = QLabel(
            'This is an Alpha version of Memority app. It might be unstable, have bugs and errors. '
            'Please keep in mind that in some cases your stored data may be lost, '
            'although we`ll do everything in our power to prevent this. \n'
            'If the app is not working, it means we`ve released an incompatible update. '
            'Please download it on our website https://memority.io/\n'
            'If you`ve encountered a bug, please send us a report to support@memority.io')
        self.log_widget = QPlainTextEdit()
        self.table_widget = TabsWidget(self)
        self.log_widget.setReadOnly(True)
        self.add_file_list_item = self.table_widget.tab_files.files_list_widget.add_item
        self.table_widget.tab_files.controls_widget.uploadButton.clicked.connect(
            self.open_file_dialog
        )

        main_layout = QVBoxLayout(container)
        main_layout.addWidget(self.msg_for_testers)
        main_layout.addWidget(self.table_widget)
        main_layout.addWidget(self.log_widget)
        container.setLayout(main_layout)

        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = int((sg.width() - widget.width()) / 4)
        y = int((sg.height() - widget.height()) / 3)
        self.move(x, y)
        asyncio.ensure_future(self.show_files())
        asyncio.ensure_future(self.refresh())
        self.show()

    async def refresh(self):
        # while True:
        await self.table_widget.refresh()
        await self.table_widget.tab_settings.refresh()
        await self.table_widget.tab_wallet.info_widget.refresh()
        await self.table_widget.tab_hosting.refresh()
        # await asyncio.sleep(5)

    def resizeEvent(self, event):
        self.log_widget.setFixedHeight(self.height() * .2)
        return super().resizeEvent(event)

    def open_file_dialog(self):
        dialog = QFileDialog()
        options = dialog.Options()
        filename, _ = dialog.getOpenFileName(self, options=options)
        # asyncio.ensure_future(self.show_progressbar())
        if filename:
            asyncio.ensure_future(self.ws_send(
                {
                    "command": "upload",
                    "kwargs": {
                        "path": filename
                    }
                }
            ))

    def download_file(self, path, hash_):
        asyncio.ensure_future(self.ws_send(
            {
                "command": "download",
                "kwargs": {
                    "destination": path,
                    "hash": hash_
                }
            }
        ))

    async def ws_handler(self):
        try:
            session = aiohttp.ClientSession()
            self._ws = await session.ws_connect(settings.daemon_address)
            async for msg in self._ws:
                if isinstance(msg, aiohttp.WebSocketError):
                    error_handler(str(msg))
                    continue
                data = json.loads(msg.data)
                process_ws_message(data, self)
        except CancelledError:
            pass
        except Exception as err:
            raven_client.captureException()
            error_handler(str(err))

    async def ws_send(self, data: dict):
        await self._ws.send_json(data)

    async def show_files(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{settings.daemon_address}/files/') as resp:
                data = await resp.json()
                process_ws_message(data, self)

    def closeEvent(self, event):
        reply = QMessageBox().question(
            self,
            "Are you sure to quit?",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            asyncio.ensure_future(self._ws.close())
            asyncio.ensure_future(self.session.close())
            for task in asyncio.Task.all_tasks():
                task.cancel()
            self.event_loop.stop()

            event.accept()

        else:
            event.ignore()


def check_first_run():
    r = requests.get(f'{settings.daemon_address}/check_first_run/')
    return r.json().get('result')


def ping_daemon():
    try:
        r = requests.get(f'{settings.daemon_address}/ping/')
        if r.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.ConnectionError:
        return False


def check_if_daemon_running():
    while True:
        daemon_running = ping_daemon()
        if daemon_running:
            break
        else:
            _app = QApplication(sys.argv)

            _ok = QMessageBox().question(
                None,
                "Is the Memority Core running?",
                f'Can`t connect to Memority Core. Is it running?\n'
                f'Please launch Memority Core before Memority UI.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            del _app
            if _ok != QMessageBox.Yes:
                sys.exit()


def unlock_account(_password):
    r = requests.post(f'{settings.daemon_address}/unlock/', json={"password": _password})
    if not r.status_code == 200:
        error_handler('Invalid password!')
        return False
    return True


if __name__ == '__main__':
    check_if_daemon_running()
    _app = QApplication(sys.argv)
    if not check_first_run():
        while True:
            password, ok = ask_for_password('Password:')
            if not ok:
                sys.exit(1)
            if not unlock_account(password):
                continue
            break
        del _app

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    try:
        main_window = MainWindow(loop)
        with contextlib.suppress(asyncio.CancelledError):
            loop.run_until_complete(main_window.ws_handler())
    except Exception as err:
        raven_client.captureException()
        error_handler(str(err))
