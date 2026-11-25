# Super Clipboard – Hinweise für Claude

## Versionierung und Changelog

Version und Changelog werden **nie von Hand** gepflegt. Bei jedem Push auf `main` liest GitHub Actions (`.github/workflows/release.yml` → `tools/release.py`) die Commit-Nachrichten seit dem letzten Tag `vX.Y.Z` und erledigt alles: neue Version, `debian/changelog`, AppStream-Einträge, Versionstabelle und Versionsnummern in `README.md`, GitHub-Release mit .deb. Die Regeln stehen in `README.md` → „Releasing a new version“ und in `tools/release.py`; dort nachsehen, nicht hier kopieren.

Deine Aufgabe ist deshalb nur eine: **die richtige Commit-Nachricht.**

### Nicht anfassen

Diese Stellen gehören dem Release-Skript. Nicht ändern, auch nicht „zur Sicherheit“:

- `VERSION = "…"` in `src/super-clipboard`
- `debian/changelog`
- `<release>`-Einträge in `data/*.metainfo.xml` und `data/*.catalog.xml`
- Versionsnummern und die Versionstabelle in `README.md`

Ausnahme: Der Nutzer verlangt ausdrücklich eine bestimmte Version (z. B. 2.0.0). Dann **nur** die `VERSION`-Zeile setzen. Setzt man auch den Changelog-Eintrag von Hand, überspringt das Skript AppStream und README.

**Durchgesetzt wird das von einem Hook**, nicht nur von diesem Text: `.claude/settings.json` ruft vor jedem Edit, Write und Bash-Befehl `tools/claude-guard.py` auf. Er blockiert Änderungen an den oben genannten Stellen, `tools/release.py` ohne `--dry-run` und `git tag` mit `vX.Y.Z`. Für die Ausnahme legt der **Nutzer** die leere Datei `.claude/allow-manual-version` an (sie hebt nur die Sperre der `VERSION`-Zeile auf; Claude darf sie nicht selbst anlegen) und löscht sie danach wieder. Blockiert der Hook, nicht umgehen (auch nicht per `sed` oder Skript), sondern die Commit-Nachricht anpassen oder den Nutzer fragen.

### Commit-Nachricht

Format: `type(scope)!: text`. Das Stage-Skill schreibt sie als eine Zeile nach `.git/CLAUDE_COMMIT_MSG`; sie muss dieses Format haben.

| Änderung | Nachricht | Ergebnis |
| --- | --- | --- |
| neue Funktion für Nutzer | `feat: …` | Minor, 1.5.0 → 1.6.0 |
| Fehler behoben, sichtbare Verbesserung | `fix: …` | Patch, 1.5.0 → 1.5.1 |
| inkompatible Änderung | `feat!: …` / `fix!: …` oder Zeile `BREAKING CHANGE:` im Text | Major, 1.5.0 → 2.0.0 |
| Doku, Aufräumen, CI, Tests, Stil | `docs:` `chore:` `refactor:` `ci:` `test:` `style:` `perf:` | kein Release |

Regeln, die sich aus dem Skript ergeben:

- **Nur `feat` und `fix` lösen ein Release aus.** Merken Nutzer die Änderung, ist es `fix:`, auch wenn es technisch ein `refactor` oder `perf` ist. Ein `BREAKING CHANGE:` im Text löst bei jedem Typ ein Major-Release aus, auch bei `docs:`.
- **Ungültige Betreffzeilen werden ohne Warnung ignoriert.** Ohne `type:` am Anfang (z. B. „Update README“) kommt die Änderung in kein Release.
- **Der Betreff ist der Changelog-Eintrag.** Jeder `feat`/`fix`-Commit wird eine Zeile in Changelog, AppStream, README und GitHub-Notes. Deshalb: Englisch, aus Nutzersicht, ein sichtbarer Effekt pro Commit. Gut: `feat: paste images as files`. Schlecht: `feat: refactor paste()`.
- **Keinen Scope verwenden, außer er sagt dem Nutzer etwas.** Er erscheint in den Release-Notes als „scope: Betreff“.
- **Betreffzeilen nie wiederverwenden.** Der Commit „feat: add language setting (Auto / English / Deutsch)“ entstand zweimal und wurde deshalb als 1.7.0 **und** 1.8.0 mit gleichem Text veröffentlicht. Ein Folge-Commit zu einem bereits eingecheckten Feature bekommt `fix:` mit neuem Wortlaut.
- **Ein Commit, eine sichtbare Änderung.** Mehrere unabhängige Änderungen vor dem Staging auf mehrere Commits aufteilen, sonst geht eine davon in der Release-Notiz unter.

### Ablauf

1. **Vor Arbeitsbeginn** `git fetch --tags` und `git status -sb`. Steht dort „hinterher“, liegt auf `origin/main` ein Release-Commit `chore(release): vX.Y.Z`, den der lokale Stand nicht hat. Erst `git pull --rebase` (bei lokalen Änderungen vorher `git stash`), sonst kollidieren Version und Changelog.
2. Änderung umsetzen, **ohne** die Dateien aus „Nicht anfassen“ zu berühren.
3. Das Stage-Skill mit passender Commit-Nachricht aufrufen. Eine Änderung an dieser Datei ist eine eigene Aufgabe mit `docs:`, sie darf nicht unter der Nachricht eines offenen `fix:`/`feat:` landen.
4. Nach dem Commit: `python3 -B tools/release.py --dry-run` zeigt die nächste Version und die Release-Notes. Das sieht nur eingecheckte Commits und nur Tags, die vom aktuellen Stand erreichbar sind; deshalb vorher Schritt 1.
5. Nach dem Push `git pull --rebase`, weil der Release-Commit auf `main` landet.

### Verboten

- `tools/release.py` **ohne `--dry-run`** lokal ausführen. Es schreibt Version, Changelog, AppStream und README um.
- Release-Tags (`vX.Y.Z`) von Hand setzen oder löschen.
- Bereits gepushte Commits mit `amend` oder `rebase` ändern.
- Committen oder pushen, ohne dass der Nutzer es verlangt hat.
