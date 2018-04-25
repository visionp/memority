#!/usr/bin/env bash

. env/bin/activate

rm -rf build dist

pyinstaller ./memority/gui/memority_gui.pyw --windowed --icon=img/icon.icns

pyinstaller ./memority/memority_core/memority_core_systray.pyw --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import raven.handlers --hidden-import raven.handlers.logging --hidden-import sqlalchemy.ext.baked --additional-hooks-dir=pyinstaller-hooks --windowed --icon=img/icon.icns

mkdir dist/memority_gui/settings
cp memority/gui/settings/defaults.yml dist/memority_gui/settings

mkdir dist/memority_core_systray/settings
mkdir dist/memority_core_systray/smart_contracts
mkdir dist/memority_core_systray/geth
cp img/icon.ico dist/memority_core_systray
cp memority/memority_core/settings/defaults.yml dist/memority_core_systray/settings
cp -r memority/memority_core/smart_contracts/binaries dist/memority_core_systray/smart_contracts
cp -r memority/memority_core/smart_contracts/binaries dist/memority_core_systray/smart_contracts
cp -r memority/memority_core/smart_contracts/install dist/memority_core_systray/smart_contracts
cp memority/memority_core/geth/darwin/geth dist/memority_core_systray/geth
