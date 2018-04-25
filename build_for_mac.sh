#!/usr/bin/env bash

. env/bin/activate

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile GUI"
pyinstaller ./memority/gui/memority_gui.pyw --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Compile Core"
pyinstaller ./memority/memority_core/memority_core_systray.pyw --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import raven.handlers --hidden-import raven.handlers.logging --hidden-import sqlalchemy.ext.baked --additional-hooks-dir=pyinstaller-hooks --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Add files to build"
mkdir dist/memority_gui.app/Contents/MacOS/settings
cp memority/gui/settings/defaults.yml dist/memority_gui.app/Contents/MacOS/settings

mkdir dist/memority_core_systray.app/Contents/MacOS/settings
mkdir dist/memority_core_systray.app/Contents/MacOS/smart_contracts
mkdir dist/memority_core_systray.app/Contents/MacOS/geth
cp img/icon.ico dist/memority_core_systray.app/Contents/MacOS
cp memority/memority_core/settings/defaults.yml dist/memority_core_systray.app/Contents/MacOS/settings
cp -r memority/memority_core/smart_contracts/binaries dist/memority_core_systray.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/binaries dist/memority_core_systray.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/install dist/memority_core_systray.app/Contents/MacOS/smart_contracts
cp memority/memority_core/geth/darwin/geth dist/memority_core_systray.app/Contents/MacOS/geth

echo "Done!"
