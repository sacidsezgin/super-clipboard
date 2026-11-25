#!/bin/sh
# Builds super-clipboard_<version>_all.deb from this tree. Needs only dpkg-deb.
set -e
cd "$(dirname "$0")"

current_version() { sed -n 's/^VERSION = "\(.*\)"$/\1/p' src/super-clipboard; }

# Local builds: the version is only bumped by the release commit that GitHub
# Actions pushes after each push to main. Fetch it first (waiting for it if
# our commits were just pushed), so the build never carries the previous
# version. Skipped in CI and with NO_SYNC=1.
if [ -z "${CI:-}" ] && [ -z "${NO_SYNC:-}" ] && git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
    sync_upstream() {
        git fetch --tags -q || { echo "warning: git fetch failed, building the local state" >&2; return 1; }
        if [ -n "$(git rev-list 'HEAD..@{u}')" ]; then
            echo "Pulling new commits from origin..."
            git pull --rebase --autostash -q
        fi
    }
    sync_upstream || true
    # Nothing unpushed and a release still planned that is not in the tree yet:
    # the workflow is running, wait for its release commit (max 5 minutes).
    tries=0
    while [ -z "$(git rev-list '@{u}..HEAD')" ] && [ "$tries" -lt 30 ]; do
        planned=$(python3 -B tools/release.py --dry-run 2>/dev/null | sed -n '1s/^Release v\([0-9][0-9.]*\) .*/\1/p')
        [ -n "$planned" ] && [ "$planned" != "$(current_version)" ] || break
        echo "Waiting for release commit v$planned from GitHub Actions... (NO_SYNC=1 skips)"
        sleep 10
        tries=$((tries + 1))
        sync_upstream || break
    done
fi

VERSION=$(current_version)
PKG="build/super-clipboard_${VERSION}_all"
rm -rf build
mkdir -p "$PKG/DEBIAN"

install -D -m 755 src/super-clipboard                       "$PKG/usr/bin/super-clipboard"
install -D -m 755 src/super-clipboard-toggle                "$PKG/usr/bin/super-clipboard-toggle"
install -D -m 755 src/super-clipboard-install-update        "$PKG/usr/lib/super-clipboard/install-update"
install -D -m 644 data/org.super_clipboard.Clipboard.desktop "$PKG/usr/share/applications/org.super_clipboard.Clipboard.desktop"
install -D -m 644 data/super-clipboard-autostart.desktop    "$PKG/etc/xdg/autostart/super-clipboard-autostart.desktop"
install -D -m 644 data/60-super-clipboard-uinput.rules      "$PKG/usr/lib/udev/rules.d/60-super-clipboard-uinput.rules"
install -D -m 644 data/super-clipboard-modules.conf         "$PKG/usr/lib/modules-load.d/super-clipboard.conf"
install -D -m 644 data/org.super_clipboard.Clipboard.update.policy "$PKG/usr/share/polkit-1/actions/org.super_clipboard.Clipboard.update.policy"
install -D -m 644 data/org.super_clipboard.Clipboard.svg    "$PKG/usr/share/icons/hicolor/scalable/apps/org.super_clipboard.Clipboard.svg"
install -D -m 644 data/super-clipboard-pin-symbolic.svg     "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-pin-symbolic.svg"
install -D -m 644 data/super-clipboard-unpin-symbolic.svg   "$PKG/usr/share/icons/hicolor/symbolic/apps/super-clipboard-unpin-symbolic.svg"
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
