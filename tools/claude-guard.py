#!/usr/bin/env python3
"""PreToolUse hook that enforces the release rules in CLAUDE.md.

Version and changelog belong to tools/release.py (run by GitHub Actions). This
hook stops Claude from editing them by hand, from running release.py for real
and from creating or deleting release tags. It reads the hook JSON on stdin and
exits 2 with a message on stderr to block the call, 0 to allow it.

Edit/Write: the file as it would be afterwards is compared with the one on
disk. Only the protected parts count, so every other edit of the same file
(for example a feature paragraph in README.md) passes.

  debian/changelog, data/*.metainfo.xml, data/*.catalog.xml   never
  src/super-clipboard                                          the VERSION line
  README.md                    version numbers and the "Version history" section

Bash: tools/release.py without --dry-run, git tag creating/deleting vX.Y.Z, and
(a heuristic, not a security boundary) in-place edits of the protected files.

Manual version, when the user asks for one: create the empty file
.claude/allow-manual-version. It lifts the VERSION-line rule only, and Claude
may not create it itself.

stdlib only; `python3 tools/claude-guard.py < payload.json` for testing.
"""

import fnmatch
import json
import os
import re
import shlex
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = ".claude/allow-manual-version"

NEVER_EDIT = ("debian/changelog", "data/*.metainfo.xml", "data/*.catalog.xml")
PROGRAM = "src/super-clipboard"
README = "README.md"

VERSION_LINE = re.compile(r'^VERSION = ".*"$', re.M)
README_VERSIONS = re.compile(
    r"This documentation describes version \d+\.\d+\.\d+"
    r"|super-clipboard_\d+\.\d+\.\d+_all\.deb"
    r"|super-clipboard-\d+\.\d+\.\d+")
HISTORY = "## Version history"
RELEASE_TAG = re.compile(r"^v\d+\.\d+\.\d+$")

HINT = " Siehe CLAUDE.md, Abschnitt 'Versionierung und Changelog': Version und Changelog erzeugt tools/release.py in GitHub Actions aus der Commit-Nachricht (feat:/fix:)."


def rel(path):
    """Path relative to the project root with forward slashes, None outside it."""
    if not path:
        return None
    full = os.path.realpath(path if os.path.isabs(path) else os.path.join(ROOT, path))
    root = os.path.realpath(ROOT)
    if full != root and not full.startswith(root + os.sep):
        return None
    return os.path.relpath(full, root).replace(os.sep, "/")


def read(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def protected_program(text):
    return VERSION_LINE.findall(text)


def protected_readme(text):
    tail = text.split(HISTORY, 1)[1] if HISTORY in text else ""
    return README_VERSIONS.findall(text), tail


def result_of(tool, data, current):
    """The file content after the edit, or None if it cannot be worked out."""
    if tool == "Write":
        return data.get("content")
    old, new = data.get("old_string"), data.get("new_string")
    if old is None or new is None or old not in current:
        return None                                   # the Edit itself will fail
    return current.replace(old, new) if data.get("replace_all") else current.replace(old, new, 1)


def check_edit(tool, data):
    path = rel(data.get("file_path") or data.get("notebook_path"))
    if path is None:
        return None
    if path == MARKER:
        return "Die Marker-Datei %s darf nur der Nutzer anlegen." % MARKER
    for pattern in NEVER_EDIT:
        if fnmatch.fnmatch(path, pattern):
            return "%s wird von tools/release.py gepflegt und nicht von Hand bearbeitet.%s" % (path, HINT)
    if path not in (PROGRAM, README):
        return None
    current = read(path)
    after = result_of(tool, data, current)
    if after is None:
        return None
    if path == PROGRAM:
        if os.path.exists(os.path.join(ROOT, MARKER)):
            return None
        if protected_program(after) != protected_program(current):
            return ("Die Zeile VERSION = \"...\" in %s wird von tools/release.py gesetzt. Nur wenn der Nutzer "
                    "ausdruecklich eine Version verlangt, legt er %s an.%s" % (PROGRAM, MARKER, HINT))
    else:
        if protected_readme(after) != protected_readme(current):
            return ("Versionsnummern und die Tabelle '%s' in %s schreibt tools/release.py. "
                    "Andere Teile der README duerfen geaendert werden.%s" % (HISTORY, README, HINT))
    return None


def segments(command):
    """Token lists of the simple commands in a shell line (split at ; | & and newlines)."""
    for part in re.split(r"&&|\|\||[;|&\n]", command):
        try:
            tokens = shlex.split(part)
        except ValueError:
            tokens = part.split()
        while tokens and re.match(r"^\w+=", tokens[0]):   # leading VAR=value
            tokens = tokens[1:]
        if tokens:
            yield tokens


def writes_to(part, name):
    """Heuristic: does this simple command write to a path containing `name`?"""
    target = r"\S*" + re.escape(name)
    if re.search(r"\b(sed|perl)\b[^|;&]*\s-[A-Za-z]*i", part):
        return True
    return bool(re.search(r"(>>?\s*|\btee\s+(-a\s+)?|\bmv\s+\S+\s+|\bcp\s+\S+\s+|\brm\s+(-\w+\s+)?)" + target, part))


def check_bash(data):
    command = data.get("command") or ""
    if MARKER in command or "allow-manual-version" in command:
        return "Die Marker-Datei %s darf nur der Nutzer anlegen." % MARKER
    for tokens in segments(command):
        program = os.path.basename(tokens[0])
        runs_release = program == "release.py" or (
            re.fullmatch(r"python[\d.]*", program) and
            any(not t.startswith("-") and os.path.basename(t) == "release.py" for t in tokens[1:]))
        if runs_release and not {"--dry-run", "-h", "--help"} & set(tokens):
            return ("tools/release.py schreibt Version, Changelog, AppStream und README um. Lokal nur mit "
                    "--dry-run ausfuehren, das echte Release macht GitHub Actions.%s" % HINT)
        if program == "git" and "tag" in tokens:
            args = tokens[tokens.index("tag") + 1:]
            listing = any(a in ("-l", "--list", "--contains", "--merged", "--no-merged", "--points-at")
                          or a.startswith("--sort") for a in args)
            if not listing and any(RELEASE_TAG.match(a) for a in args):
                return "Release-Tags vX.Y.Z setzt und loescht nur die Release-Pipeline, nicht Claude.%s" % HINT
    for part in re.split(r"&&|\|\||[;|\n]", command):
        for name in ("debian/changelog", "metainfo.xml", "catalog.xml", PROGRAM, README):
            if name not in part or not writes_to(part, name):
                continue
            if name in (PROGRAM, README) and not re.search(r"VERSION|Version history|\d+\.\d+\.\d+", part):
                continue
            return "Der Befehl scheint %s von Hand zu veraendern.%s" % (name, HINT)
    return None


def check(payload):
    tool = payload.get("tool_name")
    data = payload.get("tool_input") or {}
    if tool in ("Edit", "Write", "NotebookEdit"):
        return check_edit(tool, data)
    if tool == "Bash":
        return check_bash(data)
    return None


def main():
    try:
        payload = json.load(sys.stdin)
        message = check(payload)
    except Exception as error:                # a broken guard must not lock Claude out
        print("claude-guard: %s (nicht geprueft)" % error, file=sys.stderr)
        return 0
    if message:
        print("Blockiert: " + message, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
