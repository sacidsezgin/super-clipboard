#!/usr/bin/env python3
"""Work out and prepare the next Super Clipboard release from the commit messages.

Run by .github/workflows/release.yml on every push to main. It looks at the
commits since the last release tag (vX.Y.Z), written as conventional commits:

  fix: ...                              patch release  1.5.0 -> 1.5.1
  feat: ...                             minor release  1.5.0 -> 1.6.0
  feat!: ... or a "BREAKING CHANGE:"    major release  1.5.0 -> 2.0.0
  footer, with any type
  chore, docs, refactor, ci, test ...   no release

When a release is due it writes the new version into src/super-clipboard,
debian/changelog, the AppStream files and README.md, and the release notes
(Markdown) into the file given with --notes. --dry-run only prints the plan.

A VERSION in src/super-clipboard that is higher than the last tag is released
as it is, so any version can be set by hand: set VERSION = "2.0.0" and push.
Before the first release tag exists, the VERSION in the source is the first
release.
"""

import argparse
import datetime
import email.utils
import os
import re
import subprocess
import sys
import textwrap
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAM = "src/super-clipboard"
CHANGELOG = "debian/changelog"
APPSTREAM = ("data/org.super_clipboard.Clipboard.metainfo.xml",
             "data/org.super_clipboard.Clipboard.catalog.xml")
README = "README.md"
REPO_URL = "https://github.com/sacidsezgin/super-clipboard"

HEADER = re.compile(r"^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^()]*)\))?(?P<bang>!)?:\s*(?P<subject>\S.*)$")
BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE:", re.M)
VERSION_LINE = re.compile(r'^VERSION = "(\d+)\.(\d+)\.(\d+)"$', re.M)
SECTIONS = (("breaking", "Breaking changes"), ("feat", "Features"), ("fix", "Fixes"))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def write(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as handle:
        handle.write(text)


def parse_version(text):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    return tuple(int(part) for part in match.groups()) if match else None


def fmt(version):
    return "%d.%d.%d" % version


def source_version(text=None):
    match = VERSION_LINE.search(read(PROGRAM) if text is None else text)
    if not match:
        sys.exit('%s has no line VERSION = "X.Y.Z"' % PROGRAM)
    return tuple(int(part) for part in match.groups())


def last_release():
    """(git revision, version) the next release builds on."""
    for tag in git("tag", "--list", "v*", "--merged", "HEAD", "--sort=-v:refname").split():
        version = parse_version(tag)
        if version:
            return tag, version
    # No release tag yet: the VERSION set by hand last is the first one to publish.
    # It builds on the commit before it was set, with the VERSION found there.
    commit = git("log", "-1", "--format=%H", "-G", '^VERSION = "',
                 "--invert-grep", "--grep", r"^chore(release):", "--", PROGRAM).strip()
    try:
        before = git("show", "%s^:%s" % (commit, PROGRAM)) if commit else ""
    except subprocess.CalledProcessError:   # the first commit, or the file did not exist yet
        before = ""
    match = VERSION_LINE.search(before)
    if not match:
        return None, (0, 0, 0)
    return commit + "^", tuple(int(part) for part in match.groups())


def releasable_commits(since):
    """The fix / feat / breaking commits after `since`, oldest first."""
    log = git("log", "--reverse", "--format=%H%x1f%s%x1f%b%x1e",
              "%s..HEAD" % since if since else "HEAD")
    commits = []
    for record in log.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        sha, subject, body = (record.split("\x1f", 2) + ["", ""])[:3]
        match = HEADER.match(subject.strip())
        if not match:
            continue
        kind = match.group("type").lower()
        if match.group("bang") or BREAKING_FOOTER.search(body):
            section = "breaking"
        elif kind in ("feat", "fix"):
            section = kind
        else:
            continue
        commits.append({"sha": sha, "section": section, "scope": match.group("scope"),
                        "subject": match.group("subject").strip()})
    return commits


def bump(base, commits):
    sections = {commit["section"] for commit in commits}
    major, minor, patch = base
    if "breaking" in sections:
        return major + 1, 0, 0
    if "feat" in sections:
        return major, minor + 1, 0
    if "fix" in sections:
        return major, minor, patch + 1
    return None


def describe(commit):
    subject = commit["subject"]
    subject = subject[:1].upper() + subject[1:]
    return "%s: %s" % (commit["scope"], subject) if commit["scope"] else subject


# ------------------------------------------------------------- outputs ----

def release_notes(version, commits, since):
    lines = []
    for section, title in SECTIONS:
        entries = [commit for commit in commits if commit["section"] == section]
        if entries:
            lines.append("### " + title)
            lines += ["- %s (%s)" % (describe(commit), commit["sha"][:7]) for commit in entries]
            lines.append("")
    deb = "super-clipboard_%s_all.deb" % fmt(version)
    lines += [
        "### Install",
        "",
        "Download `%s` below and install it:" % deb,
        "",
        "```",
        "sudo apt install ./%s" % deb,
        "```",
        "",
        "Super Clipboard 1.6.0 and newer find this update by themselves and install it with one click.",
    ]
    if since and since.startswith("v"):
        lines += ["", "**Full changelog:** %s/compare/%s...v%s" % (REPO_URL, since, fmt(version))]
    return "\n".join(lines) + "\n"


def changelog_entry(text, version, commits, now):
    maintainer = re.search(r"^ -- (.+?)  ", text, re.M)
    maintainer = maintainer.group(1) if maintainer else "Sacid Sezgin <noreply@localhost>"
    package = text.split(" ", 1)[0] if text.strip() else "super-clipboard"
    bullets = []
    for commit in commits:
        line = describe(commit)
        if line[-1:] not in ".!?":
            line += "."
        bullets.append(textwrap.fill(line, width=79, initial_indent="  * ",
                                     subsequent_indent="    ", break_on_hyphens=False))
    if not bullets:
        bullets = ["  * New release."]
    return "%s (%s) unstable; urgency=medium\n\n%s\n\n -- %s  %s\n\n" % (
        package, fmt(version), "\n".join(bullets), maintainer, email.utils.format_datetime(now))


def appstream_release(text, version, base, commits, today):
    # A hand-written release still carrying the placeholder was the previous version.
    text = text.replace('version="@VERSION@"', 'version="%s"' % fmt(base))
    first = re.search(r"^([ \t]*)<release\b", text, re.M)
    if first:
        at, indent = first.start(), first.group(1)
    else:
        releases = re.search(r"^([ \t]*)<releases>\n", text, re.M)
        if not releases:
            print("warning: no <releases> in the AppStream file, left unchanged", file=sys.stderr)
            return text
        at, indent = releases.end(), releases.group(1) + "  "
    head = '%s<release version="%s" date="%s"' % (indent, fmt(version), today.isoformat())
    if commits:
        items = "\n".join("%s      <li>%s</li>" % (indent, escape(describe(commit))) for commit in commits)
        block = "%s>\n%s  <description>\n%s    <ul>\n%s\n%s    </ul>\n%s  </description>\n%s</release>\n" % (
            head, indent, indent, items, indent, indent, indent)
    else:
        block = head + "/>\n"
    return text[:at] + block + text[at:]


def update_readme(text, version, commits, today):
    """Best effort: version in the intro, install command, source archive, history table."""
    new = fmt(version)
    text = re.sub(r"(This documentation describes version )\d+\.\d+\.\d+", r"\g<1>" + new, text)
    text = re.sub(r"super-clipboard_\d+\.\d+\.\d+_all\.deb", "super-clipboard_%s_all.deb" % new, text)
    text = re.sub(r"super-clipboard-\d+\.\d+\.\d+\b", "super-clipboard-" + new, text)
    changes = "; ".join(describe(commit).replace("|", "\\|") for commit in commits) or "New release"
    row = "| %s | %s | %s |\n" % (new, today.isoformat(), changes)
    table = re.compile(r"^## Version history\n(?:.*\n)*?\| --- \| --- \| --- \|\n", re.M)
    text, found = table.subn(lambda match: match.group(0) + row, text, count=1)
    if not found:
        print("warning: no version history table in %s" % README, file=sys.stderr)
    return text


def apply(version, base, commits):
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    program = read(PROGRAM)
    write(PROGRAM, VERSION_LINE.sub('VERSION = "%s"' % fmt(version), program, count=1))
    changelog = read(CHANGELOG)
    write(CHANGELOG, changelog_entry(changelog, version, commits, now) + changelog)
    for path in APPSTREAM:
        write(path, appstream_release(read(path), version, base, commits, now.date()))
    write(README, update_readme(read(README), version, commits, now.date()))


def already_prepared(version):
    """True when an earlier run bumped the files but did not publish the release."""
    top = re.match(r"\S+ \((\d+\.\d+\.\d+)\)", read(CHANGELOG))
    return source_version() == version and bool(top) and top.group(1) == fmt(version)


def set_outputs(**values):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            for key, value in values.items():
                handle.write("%s=%s\n" % (key, value))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--notes", help="write the release notes (Markdown) to this file")
    parser.add_argument("--dry-run", action="store_true", help="only print what would be released")
    args = parser.parse_args()

    since, base = last_release()
    commits = releasable_commits(since)
    version = bump(base, commits)
    manual = source_version()
    if manual > base:
        version = max(manual, version) if version else manual
    if version is None:
        print("Nothing to release: no fix, feat or breaking commits since %s." % (since or "the start"))
        set_outputs(release="false")
        return 0

    notes = release_notes(version, commits, since)
    print("Release v%s (last release %s, %d releasable commits)" % (fmt(version), fmt(base), len(commits)))
    if args.dry_run:
        print(notes)
        return 0
    if already_prepared(version):
        print("The files already carry %s; publishing it." % fmt(version))
    else:
        apply(version, base, commits)
    if args.notes:
        with open(args.notes, "w", encoding="utf-8") as handle:
            handle.write(notes)
    set_outputs(release="true", version=fmt(version), tag="v" + fmt(version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
