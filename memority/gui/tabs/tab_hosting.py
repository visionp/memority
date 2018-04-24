import asyncio

from PyQt5.QtWidgets import *

from utils import get_address, get_host_ip


class TabHostingWidget(QWidget):

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.session = main_window.session
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.address_display = QLabel('')
        self.ip_display = QLabel('')
        self.layout.addWidget(self.address_display)
        self.layout.addWidget(self.ip_display)
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.layout.addWidget(QLabel('---under construction---'))
        self.layout.addWidget(QLabel('Space used: ...'))
        self.layout.addWidget(QLabel('Files'))
        self.layout.addWidget(QLabel('Monitoring statistics'))
        self.layout.addWidget(QLabel('---under construction---'))
        self.layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))
        asyncio.ensure_future(self.refresh())

    async def refresh(self):
        address = await get_address(self.session)
        ip = await get_host_ip(self.session) or 'Not in host list.'
        self.address_display.setText(f'Address: {address}')
        self.ip_display.setText(f'IP: {ip}')
