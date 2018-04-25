#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")"

. env/bin/activate

echo "--------------------------------------------------"
echo "Remove dirs"
rm -rf build dist

echo "--------------------------------------------------"
echo "Compile GUI"
pyinstaller ./memority/gui/memority_gui.pyw --name "Memority UI" --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Compile Core"
pyinstaller ./memority/memority_core/memority_core_systray.pyw --name "Memority Core" --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import raven.handlers --hidden-import raven.handlers.logging --hidden-import sqlalchemy.ext.baked --additional-hooks-dir=pyinstaller-hooks --windowed --icon=img/memority_icon_256.icns

echo "--------------------------------------------------"
echo "Add files to build"
mkdir dist/Memority\ UI.app/Contents/MacOS/settings
cp memority/gui/settings/defaults.yml dist/Memority\ UI.app/Contents/MacOS/settings

mkdir dist/Memority\ Core.app/Contents/MacOS/settings
mkdir dist/Memority\ Core.app/Contents/MacOS/smart_contracts
mkdir dist/Memority\ Core.app/Contents/MacOS/geth
cp img/icon.ico dist/Memority\ Core.app/Contents/MacOS
cp memority/memority_core/settings/defaults.yml dist/Memority\ Core.app/Contents/MacOS/settings
cp -r memority/memority_core/smart_contracts/binaries dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/binaries dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp -r memority/memority_core/smart_contracts/install dist/Memority\ Core.app/Contents/MacOS/smart_contracts
cp memority/memority_core/geth/darwin/geth dist/Memority\ Core.app/Contents/MacOS/geth

echo "--------------------------------------------------"
echo "Building .pkg"

VERSION="alpha-$(date +%s)"

pkgbuild --analyze --root dist/Memority\ Core.app ./dist/MemorityCoreAppComponents.plist
pkgbuild --analyze --root dist/Memority\ UI.app ./dist/MemorityUIAppComponents.plist

pkgbuild --install-location /Applications --component dist/Memority\ Core.app --identifier io.memority.pkg.memoritycore --version "${VERSION}" ./dist/Memority\ Core.pkg
pkgbuild --install-location /Applications --component dist/Memority\ UI.app --identifier io.memority.pkg.memorityui --version "${VERSION}" ./dist/Memority\ UI.pkg
pkgbuild --root dist/Memority\ UI.app --version "${VERSION}" --component-plist ./dist/MemorityUIAppComponents.plist --identifier io.memority.pkg.memorityui --install-location /Applications ./dist/Memority\ UI.pkg

productbuild --synthesize --package ./dist/Memority\ Core.pkg --package ./dist/Memority\ UI.pkg ./dist/Distribution.xml

productbuild --distribution ./dist/Distribution.xml --package-path ./dist "./Memority-alpha-${VERSION}.pkg"

echo "Done!"
