import asyncio

from PyQt5.QtWidgets import *

from utils import get_user_role
from .tab_files import TabFilesWidget
from .tab_hosting import TabHostingWidget
from .tab_settings import TabSettingsWidget
from .tab_wallet import TabWalletWidget

__all__ = ['TabsWidget']


class TabsWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.session = parent.session
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab_wallet = TabWalletWidget(self, main_window=parent)
        self.tab_files = TabFilesWidget(self, main_window=parent)
        self.tab_hosting = TabHostingWidget(self, main_window=parent)
        self.tab_settings = TabSettingsWidget(self, main_window=parent)

        self.tabs.addTab(self.tab_wallet, "Wallet")
        self.tabs.addTab(self.tab_files, "My files")
        self.tabs.addTab(self.tab_hosting, "Hosting statistics")
        self.tabs.addTab(self.tab_settings, "Settings")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        asyncio.ensure_future(self.refresh())

    async def refresh(self):
        role = await get_user_role(self.session)
        self.tabs.setTabEnabled(1, True if role in ['client', 'both'] else False)
        self.tabs.setTabEnabled(2, True if role in ['hoster', 'both'] else False)
