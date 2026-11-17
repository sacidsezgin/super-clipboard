#!/bin/sh
# Builds super-clipboard_<version>_all.deb from this tree. Needs only dpkg-deb.
set -e
cd "$(dirname "$0")"

VERSION=$(sed -n 's/^VERSION = "\(.*\)"$/\1/p' src/super-clipboard)
PKG="build/super-clipboard_${VERSION}_all"
rm -rf build
mkdir -p "$PKG/DEBIAN"

install -D -m 755 src/super-clipboard                       "$PKG/usr/bin/super-clipboard"
install -D -m 755 src/super-clipboard-toggle                "$PKG/usr/bin/super-clipboard-toggle"
install -D -m 644 data/org.super_clipboard.Clipboard.desktop "$PKG/usr/share/applications/org.super_clipboard.Clipboard.desktop"
install -D -m 644 data/super-clipboard-autostart.desktop    "$PKG/etc/xdg/autostart/super-clipboard-autostart.desktop"
install -D -m 644 data/60-super-clipboard-uinput.rules      "$PKG/usr/lib/udev/rules.d/60-super-clipboard-uinput.rules"
install -D -m 644 data/super-clipboard-modules.conf         "$PKG/usr/lib/modules-load.d/super-clipboard.conf"
install -D -m 644 data/org.super_clipboard.Clipboard.svg    "$PKG/usr/share/icons/hicolor/scalable/apps/org.super_clipboard.Clipboard.svg"
install -D -m 644 data/super-clipboard-pin-symbolic.svg     "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-pin-symbolic.svg"
install -D -m 644 data/super-clipboard-delete-symbolic.svg  "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-delete-symbolic.svg"
install -D -m 644 data/super-clipboard-settings-symbolic.svg "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-settings-symbolic.svg"
install -D -m 644 data/super-clipboard-format-symbolic.svg "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-format-symbolic.svg"
install -D -m 644 data/org.super_clipboard.Clipboard.metainfo.xml "$PKG/usr/share/metainfo/org.super_clipboard.Clipboard.metainfo.xml"
sed -i "s/@VERSION@/$VERSION/" "$PKG/usr/share/metainfo/org.super_clipboard.Clipboard.metainfo.xml"
for CATDIR in usr/share/swcatalog/xml usr/share/app-info/xmls; do
    install -D -m 644 data/org.super_clipboard.Clipboard.catalog.xml "$PKG/$CATDIR/org.super_clipboard.Clipboard.xml"
    sed -i "s/@VERSION@/$VERSION/" "$PKG/$CATDIR/org.super_clipboard.Clipboard.xml"
done
install -D -m 644 data/README.md                   "$PKG/usr/share/doc/super-clipboard/README.md"
install -D -m 644 debian/copyright                 "$PKG/usr/share/doc/super-clipboard/copyright"
install -D -m 644 debian/changelog                 "$PKG/usr/share/doc/super-clipboard/changelog"
gzip -9n "$PKG/usr/share/doc/super-clipboard/changelog"

SIZE=$(du -sk --exclude=DEBIAN "$PKG" | cut -f1)
sed -e "s/@VERSION@/$VERSION/" -e "s/@SIZE@/$SIZE/" debian/control.in > "$PKG/DEBIAN/control"
install -m 755 debian/postinst debian/prerm debian/postrm "$PKG/DEBIAN/"
echo "/etc/xdg/autostart/super-clipboard-autostart.desktop" > "$PKG/DEBIAN/conffiles"
( cd "$PKG" && find usr etc -type f -exec md5sum {} + ) > "$PKG/DEBIAN/md5sums"
chmod 644 "$PKG/DEBIAN/control" "$PKG/DEBIAN/conffiles" "$PKG/DEBIAN/md5sums"
find "$PKG" -type d -exec chmod 755 {} +

dpkg-deb --root-owner-group -Zxz --build "$PKG" "build/super-clipboard_${VERSION}_all.deb"
echo "Built build/super-clipboard_${VERSION}_all.deb"
