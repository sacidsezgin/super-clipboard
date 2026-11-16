# SuperV - clipboard history on Super+V

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
Ctrl+Enter (or the Paste button) pastes the changed text as plain text and
keeps it as a new entry, the original stays untouched. Esc goes back.
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

    superv                 start the background process (done at login)
    superv --toggle        show / hide the panel
    superv --setup-hotkey  bind Super+V again
    superv --remove-hotkey remove the binding, give Super+V back to GNOME
    superv --quit          stop the background process

## Settings

The gear button in the panel opens a settings window. Everything is stored in
`~/.config/superv/config.json`; if you edit that file by hand, restart with
`superv --quit; superv &`:

- `max_items` - entries kept, pinned ones not counted (default 50)
- `persist` - keep the history across logins (default true)
- `paste_on_select` - paste right away; false only copies (default true)
- `paste_shortcut` - `shift+insert` (default, also works in terminals),
  `ctrl+v` or `ctrl+shift+v`
- `position` - `auto` (centred on the monitor you are on) or `pointer` (at the mouse, X11 sessions only)
- `remember_position` - reopen where the panel was dragged to, stored per
  monitor in `~/.config/superv/state.json` (default true)
- `paste_formatted` - paste with formatting by default (default false)
- `expire_days` - delete unpinned entries older than this many days; 0 = never
  (default 30)

The history is stored in `~/.local/share/superv/` (readable by you only).

## How it works

- The watcher runs as an X11/XWayland client, because on GNOME Wayland only
  those are told about clipboard changes in other windows.
- Super+V is registered as a GNOME custom shortcut on first start; GNOME's
  own Super+V (notification list) is released, Super+M keeps doing that.
- Pasting sends the shortcut through a virtual keyboard (`/dev/uinput`).
  The package installs a udev rule that grants this to the local seat user.

## Uninstall

    superv --remove-hotkey
    sudo apt remove superv
    rm -rf ~/.config/superv ~/.local/share/superv
