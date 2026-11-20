# Super Clipboard – Documentation

Nov 16, 2026 · @sacidsezgin

## Overview

Super Clipboard shows your clipboard history when you press Super+V, just like Win+V on Windows 11. It runs on Zorin OS and other Ubuntu desktops (GNOME on Wayland or X11, Xfce) and comes as a single .deb package.

This documentation describes version 1.6.2 by Sacid Sezgin. The program is written in Python with GTK 3 and licensed under the MIT license.

- Remembers text and images, the last 50 entries by default.
- Pastes the chosen entry straight into the window you are working in.
- Sorts text into tabs (Text, Code, URLs, Sensitive); images get their own tab.
- Masks sensitive data such as passwords, tokens and IBANs in the display.
- Shows when each entry was copied and offers quick selection with Ctrl+1 to Ctrl+9.
- Has a preview with editing and can paste with or without formatting.
- Deletes old entries after a configurable number of days; pinned entries stay.
- Remembers the window position for each monitor separately.
- Speaks English and German. English is the default; German is used when the system language is German.
- Updates itself: it finds new releases on GitHub and installs them with one click.

## Installation and first start

Download `super-clipboard_1.6.2_all.deb` from the [latest release](https://github.com/sacidsezgin/super-clipboard/releases/latest). One command installs it with its dependencies; after that a first start is all it takes for Super+V to work.

```
sudo apt install ./super-clipboard_1.6.2_all.deb
super-clipboard --show
```

Instead of `super-clipboard --show` you can also open "Super Clipboard" from the application menu. On the first run Super Clipboard registers Super+V as a keyboard shortcut and then keeps running in the background. From the next login on it starts by itself, with a two-second delay.

**Dependencies.** apt installs these packages automatically:

- python3 (3.8 or newer), python3-gi, gir1.2-gtk-3.0, gir1.2-gdkpixbuf-2.0
- libglib2.0-bin, hicolor-icon-theme
- recommended: xwayland, udev, kmod, appstream, pkexec, ca-certificates; optional: xdotool

**The keyboard shortcut.** On GNOME, Super+V is created as a custom shortcut named "Super Clipboard History". GNOME's own binding of Super+V (notification list) is released; Super+M still opens it. On Xfce, Super Clipboard registers the shortcut through `xfconf`. To use a different key combination, open the settings (gear), click the button next to "Shortcut to open the panel", press the new keys and then "Save"; Esc cancels the capture and "Default" restores Super+V. The combination needs Ctrl, Alt or Super (or an F key). If the shortcut does nothing, run `super-clipboard --setup-hotkey`.

**Access to /dev/uinput.** Super Clipboard sends the paste key through a virtual keyboard. For this the package installs a udev rule that gives the locally logged-in user access to /dev/uinput, and loads the `uinput` module. This also means that any program running under your user can generate key presses. After installing, log out and back in once if pasting does not work right away.

## Usage

Everything can be done with the keyboard; the mouse works alongside. The window closes as soon as it loses focus.

| Key or action | Effect |
| --- | --- |
| Super+V | open or close the window |
| Up / Down arrow | select an entry |
| Page Up / Page Down | jump four entries |
| Enter or click on the entry | paste the entry (with or without formatting, depending on the setting) |
| Shift+Enter | paste the entry in the respective other format |
| Ctrl+1 to Ctrl+9 | paste the first to ninth entry of the list |
| Space | preview of the selected entry (only when the search field is empty) |
| Typing | search in the texts; the tabs stay active |
| Del | delete the selected entry (only when the search field is empty) |
| Ctrl+P | pin or unpin the entry |
| Left / Right arrow | switch tab (only when the search field is empty) |
| Ctrl+Tab | next tab; with Shift backwards |
| Esc | clear the search text, then close the window; in the preview, back to the list |
| Drag the header or footer | move the window |

**Ctrl+number in detail.** Counting happens in the list that is currently shown, including entries outside the visible area. If the list shows fewer entries than the number (other tab, search), the whole history is counted. The paste only happens when you release Ctrl.

**With the mouse.** When the pointer is over an entry, buttons appear on the right: formatting (only for formatted entries), pin, delete. "Clear all" removes all entries that are not pinned. The gear opens the settings. Unpinned entries are pushed out by newer ones once the maximum number is reached; pinned entries stay and do not count.

## Tabs and sensitive data

Every text ends up in exactly one tab, and matches for sensitive data are partly masked in the list. The sorting is based on patterns; it can be wrong, in both directions.

| Tab | What ends up there |
| --- | --- |
| All | everything, including images |
| Text | ordinary text that fits no other group |
| Code | shell commands, SQL, PHP, JavaScript, CSS, HTML/XML, JSON and similarly structured text |
| URLs | one or more web addresses (http, https, ftp, file, www), one per line and nothing else |
| Sensitive | texts in which a secret was detected |
| Images | copied images |
| Pinned (pin icon) | all pinned entries of every kind, the most recently pinned first; in the other tabs they keep their normal place in the history |

If a text falls into several groups, the order is Sensitive, URLs, Code, Text. A sentence that contains an address stays Text. Below the text of each entry you see its group (except for "Text"), "formatted" if it carries formatting, and the time it was copied.

**What counts as sensitive.**

- Passwords and keys in the form `password: value` or `DB_PASSWORD=value` (also passwort, secret, token, api key, access key and related) as well as `define('DB_PASSWORD', '…')`
- Credentials in addresses, for example `mysql://user:password@host`
- API tokens from GitHub, GitLab, Slack, AWS, Google and keys starting with `sk-`; JSON Web Tokens
- private keys in PEM format
- IBANs with a valid check digit and card numbers with a valid Luhn checksum
- single strings that look like a password: 8 to 72 characters with upper and lower case letters, a digit and a special character, or long random keys of 24 characters or more

For the last rule, `_`, `-` and `.` do not count as special characters. Names such as `Mobile_pos2` or `Report_v2.docx` therefore stay ordinary text. Email addresses, phone numbers and names are not considered sensitive. Only the first 20,000 characters of a text are examined.

**What the masking looks like.** The list shows the beginning and end of the secret with dots in between, for example `ghp_••••••••••••6789`. Multi-line secrets such as a private key appear only as dots. The masking applies to the display only:

- The real value is pasted.
- The history file contains the text unmasked.
- The search works on the real text.

## Preview and editing

The space bar opens the selected entry in full size inside the window, and text can be changed there before it is pasted. In the search field the space bar types a normal space; the preview only opens when the search field is empty.

- **Text:** shown in full. Code appears in a monospaced font.
- **Image:** scaled down to the window width, larger than in the list.
- **Paste:** Ctrl+Enter or the "Paste" button. If the text was changed, the changed version is pasted as plain text and stored as a new entry in the history. The original stays unchanged. Without changes the entry is pasted as usual, that is, with formatting if that is the default.
- **Back:** Esc or the "← Back" button.

**Sensitive entries** stay masked and read-only in the preview until you press "Show". "Hide" restores the masking.

**Limits.** For texts over 200,000 characters the preview shows only the beginning and does not allow editing; the original is pasted. The editor has no built-in undo.

## Formatting when pasting

Super Clipboard stores formatting too, and by default Enter and click paste only the plain text. An extra button pastes with the formatting.

If something was copied with formatting (bold, links, lists, for example from a web page or an office document), the entry says "formatted". To the left of the pin there is then a button with an underlined A. Only such entries have it; images and plain text do not.

| Setting "Paste with formatting by default" | Enter and click | Button next to the pin | Shift+Enter |
| --- | --- | --- | --- |
| off (default) | without formatting | with formatting | with formatting |
| on | with formatting | without formatting | without formatting |

When pasting with formatting, Super Clipboard offers the target application both forms at once, HTML and plain text. Which one is used is up to the target program: word processors and browsers can take the formatting, terminals show only the text.

For very large copies (HTML over 300,000 characters) Super Clipboard stores only the plain text. Entries without formatting do not become formatted even with the button.

## Window position and monitors

The window opens centered on the monitor you are working on, and if you move it, Super Clipboard remembers the position for exactly that monitor.

- **Which monitor?** On X11 the monitor of the active window, otherwise that of the mouse pointer. On Wayland the monitor of the mouse pointer: an invisible helper window asks the desktop where it places new windows, after which the window appears once in its place.
- **Moving:** drag the header or footer with the mouse. The position is saved per monitor in `state.json`, relative to the corner of the monitor.
- **The next time it opens,** Super Clipboard uses the remembered position for the current monitor. Monitors on which you never moved the window stay centered. If the remembered position lies outside the monitor, it is moved back into the visible area.
- **Changing monitors:** a monitor is recognized by manufacturer, model, resolution and position. If you change the arrangement of your screens, it counts as a new monitor.
- **Resetting:** use "Forget saved positions" in the settings, or turn off "Remember the panel position per monitor".

The `position` setting in `config.json` accepts `auto` (default, centered) and `pointer` (on X11 at the mouse pointer). A remembered position takes precedence in both cases.

## Settings

The most important settings are in the settings window (gear in the window header); all of them are in `~/.config/super-clipboard/config.json`. The window only changes something when you press "Save". "Cancel" or Esc discards the changes.

| Key in config.json | Default | Meaning and settings window label |
| --- | --- | --- |
| `max_items` | 50 | Number of unpinned entries, 1 to 500. Window: "Entries kept in the history" (5 to 500) |
| `expire_days` | 30 | Unpinned entries that are older are deleted; 0 = never, at most 3650. Window: "Delete entries after (days)" |
| `remember_position` | true | Remember the window position per monitor. Window: "Remember the panel position per monitor" |
| `paste_on_select` | true | Paste immediately when selecting; off = the entry is only placed on the clipboard. Window: "Paste right away when picking an entry" |
| `paste_shortcut` | `shift+insert` | Key that Super Clipboard sends to paste: `shift+insert`, `ctrl+v` or `ctrl+shift+v`. Window: "Shortcut used for pasting" |
| `paste_formatted` | false | Paste with formatting by default. Window: "Paste with formatting by default" |
| `persist` | true | Keep the history after logging out. Window: "Keep the history after logging out" |
| `hotkey` | `<Super>v` | Keyboard shortcut that opens the window, as a GTK accelerator such as `<Primary><Alt>k`. Window: "Shortcut to open the panel" |
| `check_updates` | true | Look for new releases on GitHub at startup and every 12 hours. Window: "Check for updates automatically" |
| `position` | `auto` | `auto` = centered on the monitor, `pointer` = at the mouse pointer (X11 only); file only |
| `max_text_chars` | 1000000 | longer texts are not recorded; file only |
| `max_image_pixels` | 40000000 | images with more pixels (width times height) are not recorded; file only |
| `max_html_chars` | 300000 | larger formatting is discarded, the text stays; file only |

**Good to know.**

- Pasting with `shift+insert` (default) also works in terminals. For this, Super Clipboard additionally sets the mouse selection (primary selection) to the plain text.
- When saving in the window, surplus or too old entries are deleted immediately. Super Clipboard also checks the age at startup, when the window opens, and every hour.
- If you edited `config.json` by hand, restart: `super-clipboard --quit; super-clipboard &`. If the file is missing, Super Clipboard creates it with the default values at startup.

## Files, storage location and privacy

Super Clipboard stores everything locally in your home directory. Its only network connection is the update check (see "Updates and uninstallation"), which sends nothing but the installed version number; turn off "Check for updates automatically" to stop it. The folders are readable only by you (permissions 700), and so are the files (600).

| Path | Content |
| --- | --- |
| `~/.local/share/super-clipboard/history.json` | the history: text, formatting (HTML) if any, pin status, time; sensitive texts unmasked |
| `~/.local/share/super-clipboard/images/` | copied images as PNG |
| `~/.config/super-clipboard/config.json` | settings |
| `~/.config/super-clipboard/state.json` | remembered window positions per monitor; the last version that ran and the last update that was announced |
| `~/.config/super-clipboard/hotkey-installed` | marker that the keyboard shortcut has already been registered |
| `~/.cache/super-clipboard/updates/` | the last downloaded update package and `install.log` from installing it |

**What is not recorded.**

- Copies that a password manager marks as confidential (`x-kde-passwordManagerHint`). KeePassXC does this; whether another manager does depends on that manager.
- Empty texts or texts consisting only of whitespace.
- Texts over 1,000,000 characters and images over 40 million pixels (adjustable in `config.json`).

**Deleting the history.** "Clear all" removes everything except pinned entries. To delete everything, run `super-clipboard --quit` and remove `~/.local/share/super-clipboard`. If you do not want the history on disk, turn off "Keep the history after logging out"; Super Clipboard then writes no history.json. Copied images still sit in the images folder while running and are deleted at the next start.

## Commands

All commands go through the `super-clipboard` program and talk to the background process that is already running.

| Command | Effect |
| --- | --- |
| `super-clipboard` | start the background process (done by the autostart entry at login), without showing the window |
| `super-clipboard --show` (`-s`) | show the window; starts the process if it is not running |
| `super-clipboard --toggle` (`-t`) | show or hide the window |
| `super-clipboard --quit` (`-q`) | end the background process and save the history |
| `super-clipboard --setup-hotkey` | (re)register the keyboard shortcut (Super+V unless changed in the settings) |
| `super-clipboard --remove-hotkey` | remove the keyboard shortcut and give Super+V back to GNOME |
| `super-clipboard --version` (`-v`) | print the version |
| `super-clipboard --check-update` | ask GitHub whether a newer version exists and print the answer |
| `super-clipboard-toggle` | called by the keyboard shortcut; toggles the window over D-Bus and starts Super Clipboard if it is not running |

## How it works

A small background process watches the clipboard; the window is only its display. The path of an entry:

1. You copy something. The process notices the change of clipboard owner and reads which formats are offered.
2. If the copy carries the password-manager hint, it is discarded. Otherwise Super Clipboard reads text (and, if present, `text/html`) or an image.
3. The text is sorted (Sensitive, URLs, Code, Text) and stored. The same text is not stored twice but moved to the front with a new time.
4. Super+V calls `super-clipboard-toggle`, which opens the window over D-Bus. The window shows the history.
5. On selection, Super Clipboard puts the entry on the clipboard, closes the window and, after about 0.2 seconds, sends the paste key through a virtual keyboard.

**Building blocks and reasons.**

- **X11 even on Wayland.** The process runs as an X11 program (through XWayland), because under GNOME on Wayland only such programs learn what is copied in other windows.
- **Virtual keyboard.** Pasting goes through `/dev/uinput`, because Wayland does not allow sending key presses into other windows. Only on X11 is there `xdotool` as a fallback.
- **Formatting.** An invisible widget takes over the clipboard and answers requests with both HTML and plain text.
- **Window without flicker.** It only becomes visible once it is in place; on Wayland an invisible 1×1 window determines the monitor beforehand.
- **Keyboard shortcut.** Registered as a custom GNOME shortcut that starts `super-clipboard-toggle`.
- **Metadata for software centers.** The package contains AppStream data (name "Super Clipboard", developer, release notes).
- **Updates.** The process asks the GitHub API (`api.github.com`) for the latest release; the request carries only `super-clipboard/<version>` as its user agent. A newer package is downloaded from the release, checked against its SHA-256 checksum and handed to `/usr/lib/super-clipboard/install-update`. pkexec runs that helper as root under the polkit action `org.super_clipboard.Clipboard.update`, which asks for an administrator password. The helper installs only packages named `super-clipboard`, through apt.

## Limits and known restrictions

Super Clipboard is a small tool, and some things it cannot do, by design or for technical reasons.

- **Files.** Super Clipboard does not store copied files as files; depending on the file manager, at most their path appears as text.
- **Formatting.** Only HTML is stored, no RTF. Whether the target application accepts the formatting is up to that application.
- **Detection of sensitive data.** It is based on patterns and is sometimes wrong. There is no manual re-sorting. The masking protects only the display, not the file and not the search.
- **Password managers.** Only copies with a confidentiality hint are skipped. Without the hint, Super Clipboard records what was copied.
- **Pasting without /dev/uinput.** On Wayland Super Clipboard then cannot send a key. The entry is on the clipboard, and the footer of the window says that you must paste yourself with Ctrl+V. On X11, `xdotool` helps.
- **Window on Wayland.** It appears centered on the monitor with the mouse pointer; placing it at the pointer is only available on X11. Whether the window gets keyboard focus immediately when opening is decided by the desktop.
- **Monitors.** If you change the arrangement of your screens, Super Clipboard starts centered again for the monitor changed that way; the old position is then no longer assigned.
- **Editor.** The preview has no undo; texts over 200,000 characters cannot be edited there.
- **Software center.** If you open the .deb file in the software app, it shows the package name `super-clipboard` (Debian does not allow capital letters). After installation the application is called "Super Clipboard".

## Troubleshooting

Most problems concern the keyboard shortcut or pasting. Messages from the program appear in the terminal if you start it there: `super-clipboard --quit; super-clipboard`.

| Problem | Cause and solution |
| --- | --- |
| Super+V does nothing | Run `super-clipboard --setup-hotkey`. Check whether the process is running (`pgrep -af super-clipboard`) and whether another shortcut in Settings > Keyboard uses Super+V. |
| Window opens, but nothing is pasted | If the footer says "Entry is copied on Enter – then paste with Ctrl+V", access to `/dev/uinput` is missing. Log out and back in once; `ls -l /dev/uinput` shows whether the permission is set. On X11, `sudo apt install xdotool` helps. |
| Nothing or the wrong thing arrives in a terminal | The default is `shift+insert`. If the program needs a different key, set "Shortcut used for pasting" to `ctrl+shift+v` in the settings. |
| Window appears on the wrong monitor | Use "Forget saved positions" in the settings. On Wayland the mouse pointer decides, on X11 the active window. |
| Entry is wrongly sensitive or not sensitive | This is down to the pattern detection. Deleting and copying again changes nothing, because the text is sorted the same way again; a correction per entry is not provided. |
| History is empty after login | Check whether "Keep the history after logging out" is on and whether `expire_days` has already deleted the entries. |
| The software app shows an old version or the name `super-clipboard` | For the installed application run `gnome-software --quit` and reopen the app; if necessary log out and back in. For an opened .deb file see "Limits". |
| "Could not check for updates" | No network connection, or GitHub's limit for anonymous requests (60 per hour per address) was reached. The next check runs by itself; `super-clipboard --check-update` shows the error. |
| "Update failed: … Could not get lock …" | Another software update is running. Wait until it has finished, then press "Try again". |
| "Update" fails or no password dialog appears | The details are in `~/.cache/super-clipboard/updates/install.log`. Without a password dialog the desktop has no polkit agent; install the update by hand (see "Updates and uninstallation"). |
| The interface is in the wrong language | Super Clipboard follows the system language (`LC_ALL`, `LC_MESSAGES`, `LANG`, and a `LANGUAGE` preference list). German systems get German, everything else gets English. Restart with `super-clipboard --quit; super-clipboard` after changing it, for example `LANG=en_US.UTF-8 super-clipboard`. |

## Updates and uninstallation

An update replaces only the program; history and settings are kept.

**Automatic updates.** Super Clipboard asks GitHub for the newest release 90 seconds after it starts and then every 12 hours. When there is a newer version:

- a notification says so once, with an "Update" button;
- the window shows a bar at the top with the new version (click the number for the release notes) and an "Update" button;
- the settings show it next to the "Update to …" button.

"Update" downloads the .deb from the GitHub release, checks its SHA-256 checksum and installs it. The system asks for an administrator password first. Afterwards the new version starts by itself and a notification confirms the update. If you close the password dialog, nothing is installed and the bar stays.

To stop the automatic check, turn off "Check for updates automatically" in the settings; "Check now" still checks on request, and `super-clipboard --check-update` checks from the terminal. When Super Clipboard runs from the source folder or pkexec is missing, "Update" opens the release page instead.

**Manual update.** Download the new .deb from the [releases page](https://github.com/sacidsezgin/super-clipboard/releases) and install it with the same command. The installation ends the running process; the next press of Super+V or the next login starts the new version.

```
sudo apt install ./super-clipboard_<version>_all.deb
super-clipboard --quit; super-clipboard --show
```

**Uninstallation.**

```
super-clipboard --remove-hotkey
sudo apt remove super-clipboard
rm -rf ~/.config/super-clipboard ~/.local/share/super-clipboard
```

The first command gives Super+V back to GNOME. The last line deletes history and settings; without it both remain for a later reinstallation.

## Building from source

Every GitHub release also offers the source code (`super-clipboard-1.6.2.tar.gz`). It builds a .deb with a single script; besides the standard tools it only needs `dpkg-deb`.

```
tar xzf super-clipboard-1.6.2.tar.gz
cd super-clipboard-1.6.2
./build.sh
```

The result is at `build/super-clipboard_<version>_all.deb`. The script reads the version from the line `VERSION = "…"` in `src/super-clipboard`.

| Folder or file | Content |
| --- | --- |
| `src/super-clipboard` | the program (a single Python file) |
| `src/super-clipboard-toggle` | small script that the keyboard shortcut calls |
| `src/super-clipboard-install-update` | root helper that installs a downloaded update (run through pkexec) |
| `data/` | desktop entries, icons, udev rule, polkit policy, AppStream files, README |
| `debian/` | package data: `control.in`, `postinst`, `prerm`, `postrm`, `changelog`, `copyright` |
| `build.sh` | builds the package |
| `tools/release.py` | works out the next version from the commit messages and updates the files for it |
| `.github/workflows/release.yml` | builds and publishes a GitHub release on every push to `main` that needs one |

**Releasing a new version.** Releases happen by themselves: on every push to `main`, GitHub Actions reads the commit messages since the last release tag, written as [Conventional Commits](https://www.conventionalcommits.org/):

| Commit message | Release |
| --- | --- |
| `fix: …` | patch release, 1.5.0 → 1.5.1 |
| `feat: …` | minor release, 1.5.0 → 1.6.0 |
| `feat!: …`, `fix!: …` or a `BREAKING CHANGE:` line in the body | major release, 1.5.0 → 2.0.0 |
| `chore:`, `docs:`, `refactor:`, `ci:`, `test:`, `style:` … | no release |

For a release, `tools/release.py` raises `VERSION` in `src/super-clipboard`, adds an entry built from the commit subjects to `debian/changelog`, the AppStream files and the version history below, and updates the version numbers in this README. The workflow builds the .deb, commits these changes to `main` as `chore(release): vX.Y.Z` and publishes the GitHub release `vX.Y.Z` with `super-clipboard_X.Y.Z_all.deb` and its `.sha256` file attached.

- Pull after a release (`git pull --rebase`), because the release commit lands on `main`.
- The commit subjects become the release notes, so write them for users: `feat: paste images as files`, not `feat: refactor paste()`.
- To release a version by hand, set it in `src/super-clipboard` (for example `VERSION = "2.0.0"`) and push; a `VERSION` above the last tag is released as it is.
- Until the first release tag exists, the `VERSION` in `src/super-clipboard` is published as the first release.
- `python3 tools/release.py --dry-run` shows what the next release would be.
- If `main` is a protected branch, allow GitHub Actions to push to it; otherwise the release commit is refused and no release is made.

**Languages.** The interface strings live in the `STRINGS` table in `src/super-clipboard`. `DEFAULT_LANGUAGE` (`en`) is used for every system language without a translation. To add a language, add a table under its two-letter code with the same keys as `en`.

## Version history

| Version | Date | Changes |
| --- | --- | --- |
| 1.6.2 | 2026-11-20 | The pin button is no longer shown on every entry in the Pinned tab |
| 1.6.1 | 2026-11-20 | Added unpin button hover |
| 1.6.0 | 2026-11-18 | Finds new versions on GitHub and installs them with one click (administrator password); "Check for updates automatically" setting and `--check-update`; every fix and feature is published as a GitHub release with the .deb |
| 1.5.0 | 2026-11-17 | "Pinned" tab (pin icon) with all pinned entries, the most recently pinned first |
| 1.4.0 | 2026-11-17 | Keyboard shortcut that opens the window can be changed in the settings |
| 1.3.1 | 2026-11-17 | Old SuperV shortcut is removed on first start so it no longer blocks Super+V; window shadow no longer cut off |
| 1.3.0 | 2026-11-16 | Renamed from SuperV to Super Clipboard; English is the default interface language, German follows a German system language; language detection follows gettext rules; documentation in English |
| 1.2.0 | 2026-11-16 | Preview with editing (space bar); pasting with or without formatting, button next to the pin and a setting; release notes for the software center |
| 1.1.1 | 2026-11-16 | Window no longer flashes before it is placed; Ctrl+number waits for Ctrl to be released; "URLs" tab; names such as `Mobile_pos2` no longer count as a password |
| 1.1.0 | 2026-11-16 | Quick selection with Ctrl+1 to 9; time per entry; remember position per monitor; automatic deletion; Text, Code, Sensitive, Images tabs with masking; settings window |
| 1.0.7 | 2026-11-13 | Version number centered in the window header |
| 1.0.6 | 2026-11-13 | Version number instead of author in the window header |
| 1.0.5 | 2026-11-13 | AppStream catalog data for the name "SuperV"; grab cursor removed |
| 1.0.4 | 2026-11-13 | Package description with name and author |
| 1.0.3 | 2026-11-13 | Window can be moved with the mouse; AppStream metadata |
| 1.0.2 | 2026-11-13 | Author credit |
| 1.0.1 | 2026-11-13 | Highlighted row display fixed; opening on the current monitor |
| 1.0.0 | 2026-11-13 | first version: history for text and images, Super+V, search, pinning |
