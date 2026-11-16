#!/bin/sh
# Builds superv_<version>_all.deb from this tree. Needs only dpkg-deb.
set -e
cd "$(dirname "$0")"

VERSION=$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' src/superv)
PKG="build/superv_${VERSION}_all"
rm -rf build
mkdir -p "$PKG/DEBIAN"

install -D -m 755 src/superv                       "$PKG/usr/bin/superv"
install -D -m 755 src/superv-toggle                "$PKG/usr/bin/superv-toggle"
install -D -m 644 data/org.superv.Clipboard.desktop "$PKG/usr/share/applications/org.superv.Clipboard.desktop"
install -D -m 644 data/superv-autostart.desktop    "$PKG/etc/xdg/autostart/superv-autostart.desktop"
install -D -m 644 data/60-superv-uinput.rules      "$PKG/usr/lib/udev/rules.d/60-superv-uinput.rules"
install -D -m 644 data/superv-modules.conf         "$PKG/usr/lib/modules-load.d/superv.conf"
install -D -m 644 data/org.superv.Clipboard.svg    "$PKG/usr/share/icons/hicolor/scalable/apps/org.superv.Clipboard.svg"
install -D -m 644 data/superv-pin-symbolic.svg     "$PKG/usr/share/icons/hicolor/symbolic/apps/superv-pin-symbolic.svg"
install -D -m 644 data/superv-delete-symbolic.svg  "$PKG/usr/share/icons/hicolor/symbolic/apps/superv-delete-symbolic.svg"
install -D -m 644 data/superv-settings-symbolic.svg "$PKG/usr/share/icons/hicolor/symbolic/apps/superv-settings-symbolic.svg"
install -D -m 644 data/superv-format-symbolic.svg "$PKG/usr/share/icons/hicolor/symbolic/apps/superv-format-symbolic.svg"
install -D -m 644 data/org.superv.Clipboard.metainfo.xml "$PKG/usr/share/metainfo/org.superv.Clipboard.metainfo.xml"
sed -i "s/@VERSION@/$VERSION/" "$PKG/usr/share/metainfo/org.superv.Clipboard.metainfo.xml"
for CATDIR in usr/share/swcatalog/xml usr/share/app-info/xmls; do
    install -D -m 644 data/org.superv.Clipboard.catalog.xml "$PKG/$CATDIR/org.superv.Clipboard.xml"
    sed -i "s/@VERSION@/$VERSION/" "$PKG/$CATDIR/org.superv.Clipboard.xml"
done
install -D -m 644 data/README.md                   "$PKG/usr/share/doc/superv/README.md"
install -D -m 644 debian/copyright                 "$PKG/usr/share/doc/superv/copyright"
install -D -m 644 debian/changelog                 "$PKG/usr/share/doc/superv/changelog"
gzip -9n "$PKG/usr/share/doc/superv/changelog"

SIZE=$(du -sk --exclude=DEBIAN "$PKG" | cut -f1)
sed -e "s/@VERSION@/$VERSION/" -e "s/@SIZE@/$SIZE/" debian/control.in > "$PKG/DEBIAN/control"
install -m 755 debian/postinst debian/prerm debian/postrm "$PKG/DEBIAN/"
echo "/etc/xdg/autostart/superv-autostart.desktop" > "$PKG/DEBIAN/conffiles"
( cd "$PKG" && find usr etc -type f -exec md5sum {} + ) > "$PKG/DEBIAN/md5sums"
chmod 644 "$PKG/DEBIAN/control" "$PKG/DEBIAN/conffiles" "$PKG/DEBIAN/md5sums"
find "$PKG" -type d -exec chmod 755 {} +

dpkg-deb --root-owner-group -Zxz --build "$PKG" "build/superv_${VERSION}_all.deb"
echo "Built build/superv_${VERSION}_all.deb"
