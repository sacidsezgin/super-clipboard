# Super Clipboard - clipboard history on Super+V

By Sacid Sezgin.

A small clipboard history panel in the style of the Windows 11 Win+V flyout,
for Zorin OS (GNOME, Wayland or X11) and other Ubuntu-based desktops.

## Use

| Key            | Action                                        |
| -------------- | --------------------------------------------- |
| Super+V        | open / close the panel                        |
| Up / Down      | move through the entries                      |
| Enter or click | paste the entry into the window you came from |
| just type      | filter the text entries                       |
| Ctrl+P         | pin / unpin (pinned entries survive "Clear all") |
| Space          | preview of the entry (full text or large image); while the search field has text, Space is just a space |
| Shift+Enter    | paste the other way (with formatting if plain is the default, and vice versa) |
| Ctrl+1 … Ctrl+9 | paste the first … ninth entry of the list (scrolled-out ones too; if the tab shows fewer, the whole history is counted) |
| Left / Right   | switch tab (while the search field is empty); Ctrl+Tab always |
| Del            | remove the entry                              |
| Esc            | close                                         |
| drag header    | move the panel                                |

Text and images are recorded. Entries that a password manager marks as
secret (KeePassXC and others) are skipped.

## Preview and editing

Space opens the selected entry in the panel. Text can be changed there;
changes are saved into the entry itself (pinned entries stay pinned) with the
Save button or Ctrl+S, and also on Esc, Back, paste or when the panel closes.
Ctrl+Enter (or the Paste button) saves and pastes it. Esc goes back.
Sensitive entries are shown masked, "Show" reveals and unlocks them.

## Formatting

If a copy carried formatting (bold, links, lists ... as copied from a web page
or an office document) the entry says "formatted" and has an extra button
left of the pin. By default Enter and a click paste plain text and that button
pastes with formatting; the setting "Paste with formatting by default" (gear
button) swaps the two. Entries without formatting are always pasted as plain text.

## Tabs

Every text entry is sorted into one tab: **Text**, **Code**, **URLs** or **Sensitive**;
images go to **Images**, **All** shows everything. The sorting is pattern
matching and can be wrong in both directions.

Sensitive means: passwords and secrets in `key=value` form, API tokens,
private keys, credentials inside URLs, IBANs, card numbers, and single strings
that look like a password. These entries are shown partly masked in the list.
Pasting inserts the real value, and the history file still holds it in full
(readable by you only).

## Commands

    super-clipboard                 start the background process (done at login)
    super-clipboard --toggle        show / hide the panel
    super-clipboard --setup-hotkey  bind Super+V again
    super-clipboard --remove-hotkey remove the binding, give Super+V back to GNOME
    super-clipboard --quit          stop the background process
    super-clipboard --check-update  ask GitHub whether a newer version exists

## Settings

The gear button in the panel opens a settings window. Everything is stored in
`~/.config/super-clipboard/config.json`; if you edit that file by hand, restart with
`super-clipboard --quit; super-clipboard &`:

- `max_items` - entries kept, pinned ones not counted (default 50)
- `persist` - keep the history across logins (default true)
- `hotkey` - shortcut that opens the panel, as a GTK accelerator (default `<Super>v`);
  easiest to change with the "Shortcut to open the panel" button in the settings window
- `paste_on_select` - paste right away; false only copies (default true)
- `paste_shortcut` - `shift+insert` (default, also works in terminals),
  `ctrl+v` or `ctrl+shift+v`
- `position` - `auto` (centred on the monitor you are on) or `pointer` (at the mouse, X11 sessions only)
- `remember_position` - reopen where the panel was dragged to, stored per
  monitor in `~/.config/super-clipboard/state.json` (default true)
- `paste_formatted` - paste with formatting by default (default false)
- `expire_days` - delete unpinned entries older than this many days; 0 = never
  (default 30)
- `check_updates` - look for new releases on GitHub at startup and every 12 hours
  (default true)

The history is stored in `~/.local/share/super-clipboard/` (readable by you only).

## How it works

- The watcher runs as an X11/XWayland client, because on GNOME Wayland only
  those are told about clipboard changes in other windows.
- Super+V is registered as a GNOME custom shortcut on first start; GNOME's
  own Super+V (notification list) is released, Super+M keeps doing that.
- Pasting sends the shortcut through a virtual keyboard (`/dev/uinput`).
  The package installs a udev rule that grants this to the local seat user.

## Updates

Super Clipboard asks GitHub for the newest release shortly after it starts and
then every 12 hours; that request is its only network connection. When there
is a newer version, a notification and a bar at the top of the panel offer an
"Update" button. It downloads the .deb, checks its SHA-256 checksum and
installs it after asking for an administrator password (pkexec); the new
version then starts by itself. Turn the check off with "Check for updates
automatically" in the settings. Releases: https://github.com/sacidsezgin/super-clipboard/releases

## Uninstall

    super-clipboard --remove-hotkey
    sudo apt remove super-clipboard
    rm -rf ~/.config/super-clipboard ~/.local/share/super-clipboard
