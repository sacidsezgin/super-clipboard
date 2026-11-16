# SuperV – Dokumentation

Nov 16, 2026 · @Sacid

## Überblick

SuperV zeigt mit Super+V den Verlauf der Zwischenablage an, so wie Win+V unter Windows 11. Es läuft unter Zorin OS und anderen Ubuntu-Desktops (GNOME mit Wayland oder X11, Xfce) und kommt als einzelnes .deb-Paket.

Diese Dokumentation beschreibt Version 1.2.0 von Sacid Sezgin. Das Programm ist in Python mit GTK 3 geschrieben, die Lizenz ist MIT.

- Merkt sich Text und Bilder, standardmäßig die letzten 50 Einträge.
- Fügt den gewählten Eintrag direkt in das Fenster ein, in dem Sie gerade arbeiten.
- Sortiert Texte in Reiter (Text, Code, URLs, Sensibel); Bilder haben einen eigenen Reiter.
- Zensiert sensible Daten wie Passwörter, Tokens und IBANs in der Anzeige.
- Zeigt bei jedem Eintrag, wann er kopiert wurde, und bietet Schnellwahl mit Strg+1 bis Strg+9.
- Hat eine Vorschau mit Bearbeiten und kann mit oder ohne Formatierung einfügen.
- Löscht alte Einträge nach einer einstellbaren Zahl von Tagen; angeheftete bleiben.
- Merkt sich die Fensterposition für jeden Monitor einzeln.
- Spricht Deutsch und Englisch, je nach Systemsprache.

## Installation und Start

Ein Befehl installiert SuperV samt Abhängigkeiten; danach genügt ein erster Start, damit Super+V funktioniert.

```
sudo apt install ./superv_1.2.0_all.deb
superv --show
```

Statt `superv --show` können Sie auch „SuperV“ im Anwendungsmenü öffnen. Bei der ersten Ausführung trägt SuperV Super+V als Tastenkürzel ein und läuft danach im Hintergrund. Ab dem nächsten Login startet es von selbst, mit zwei Sekunden Verzögerung.

**Abhängigkeiten.** apt installiert diese Pakete automatisch mit:

- python3 (ab 3.8), python3-gi, gir1.2-gtk-3.0, gir1.2-gdkpixbuf-2.0
- libglib2.0-bin, hicolor-icon-theme
- empfohlen: xwayland, udev, kmod, appstream; optional: xdotool

**Das Tastenkürzel.** Unter GNOME wird Super+V als eigenes Kürzel „SuperV Clipboard History“ angelegt. GNOMEs eigene Belegung von Super+V (Benachrichtigungsliste) wird freigegeben; Super+M öffnet sie weiterhin. Unter Xfce trägt SuperV das Kürzel über `xfconf` ein. Tut Super+V nichts, hilft `superv --setup-hotkey`.

**Zugriff auf /dev/uinput.** SuperV schickt die Einfügetaste über eine virtuelle Tastatur. Dafür installiert das Paket eine udev-Regel, die /dev/uinput dem lokal angemeldeten Benutzer freigibt, und lädt das Modul `uinput`. Das heißt auch: Jedes Programm, das unter Ihrem Benutzer läuft, kann damit Tastendrücke erzeugen. Nach der Installation einmal ab- und wieder anmelden, falls das Einfügen nicht gleich klappt.

## Bedienung

Alles lässt sich mit der Tastatur erledigen; die Maus geht parallel. Das Fenster schließt sich, sobald es den Fokus verliert.

| Taste oder Aktion | Wirkung |
| --- | --- |
| Super+V | Fenster öffnen oder schließen |
| Pfeil hoch / runter | Eintrag wählen |
| Bild hoch / runter | vier Einträge weiter springen |
| Enter oder Klick auf den Eintrag | Eintrag einfügen (mit oder ohne Formatierung, je nach Einstellung) |
| Umschalt+Enter | Eintrag mit dem jeweils anderen Format einfügen |
| Strg+1 bis Strg+9 | ersten bis neunten Eintrag der Liste einfügen |
| Leertaste | Vorschau des gewählten Eintrags (nur bei leerem Suchfeld) |
| Tippen | Suche in den Texten; die Reiter bleiben aktiv |
| Entf | gewählten Eintrag löschen (nur bei leerem Suchfeld) |
| Strg+P | Eintrag anheften oder lösen |
| Pfeil links / rechts | Reiter wechseln (nur bei leerem Suchfeld) |
| Strg+Tab | nächster Reiter; mit Umschalt rückwärts |
| Esc | Suchtext löschen, danach Fenster schließen; in der Vorschau zurück zur Liste |
| Kopfzeile oder Fußzeile ziehen | Fenster verschieben |

**Strg+Zahl im Detail.** Gezählt wird in der Liste, die gerade angezeigt wird, auch bei Einträgen außerhalb des sichtbaren Bereichs. Zeigt die Liste weniger Einträge als die Zahl (anderer Reiter, Suche), zählt der gesamte Verlauf. Eingefügt wird erst, wenn Sie Strg loslassen.

**Mit der Maus.** Fährt der Zeiger über einen Eintrag, erscheinen rechts Knöpfe: Formatierung (nur bei formatierten Einträgen), Anheften, Löschen. „Alle löschen“ entfernt alle Einträge, die nicht angeheftet sind. Das Zahnrad öffnet die Einstellungen. Nicht angeheftete Einträge werden von neueren verdrängt, sobald die Höchstzahl erreicht ist; angeheftete bleiben und zählen nicht mit.

## Reiter und sensible Daten

Jeder Text landet in genau einem Reiter, und Treffer für sensible Daten werden in der Liste teilweise unkenntlich gemacht. Die Einsortierung beruht auf Mustern; sie kann sich irren, in beide Richtungen.

| Reiter | Was dort landet |
| --- | --- |
| Alle | alles, auch Bilder |
| Text | normaler Text, der in keine andere Gruppe passt |
| Code | Shell-Befehle, SQL, PHP, JavaScript, CSS, HTML/XML, JSON und ähnlich aufgebauter Text |
| URLs | eine oder mehrere Web-Adressen (http, https, ftp, file, www), eine pro Zeile und sonst nichts |
| Sensibel | Texte, in denen ein Geheimnis erkannt wurde |
| Bilder | kopierte Bilder |

Fällt ein Text in mehrere Gruppen, gilt die Reihenfolge Sensibel, URLs, Code, Text. Ein Satz, in dem eine Adresse vorkommt, bleibt Text. Zu jedem Eintrag steht unter dem Text die Gruppe (außer bei „Text“), „formatiert“ falls er Formatierung trägt, und die Zeit des Kopierens.

**Was als sensibel gilt.**

- Passwörter und Schlüssel in der Form `passwort: wert` oder `DB_PASSWORD=wert` (auch password, secret, token, api key, access key und Verwandte) sowie `define('DB_PASSWORD', '…')`
- Zugangsdaten in Adressen, etwa `mysql://benutzer:passwort@host`
- API-Tokens von GitHub, GitLab, Slack, AWS, Google und mit `sk-` beginnende Schlüssel; JSON Web Tokens
- private Schlüssel im PEM-Format
- IBANs mit gültiger Prüfziffer und Kartennummern mit gültiger Luhn-Prüfsumme
- einzelne Zeichenketten, die wie ein Passwort aussehen: 8 bis 72 Zeichen mit Groß- und Kleinbuchstaben, Ziffer und Sonderzeichen, oder lange Zufallsschlüssel ab 24 Zeichen

Bei der letzten Regel zählen `_`, `-` und `.` nicht als Sonderzeichen. Namen wie `Mobile_pos2` oder `Report_v2.docx` bleiben deshalb normaler Text. E-Mail-Adressen, Telefonnummern und Namen gelten nicht als sensibel. Untersucht werden nur die ersten 20.000 Zeichen eines Textes.

**Wie die Zensur aussieht.** Die Liste zeigt Anfang und Ende des Geheimnisses und Punkte dazwischen, zum Beispiel `ghp_••••••••••••6789`. Mehrzeilige Geheimnisse wie ein privater Schlüssel erscheinen nur als Punkte. Die Zensur gilt ausschließlich für die Anzeige:

- Eingefügt wird der echte Wert.
- Die Verlaufsdatei enthält den Text unzensiert.
- Die Suche arbeitet auf dem echten Text.

## Vorschau und Bearbeiten

Die Leertaste öffnet den gewählten Eintrag in voller Größe im Fenster, und Text lässt sich dort ändern, bevor er eingefügt wird. In der Suche tippt die Leertaste ein normales Leerzeichen; die Vorschau öffnet sich nur bei leerem Suchfeld.

- **Text:** wird vollständig gezeigt. Code erscheint in Festbreitenschrift.
- **Bild:** wird auf die Fensterbreite verkleinert, größer als in der Liste.
- **Einfügen:** Strg+Enter oder der Knopf „Einfügen“. Wurde der Text geändert, wird die geänderte Fassung als reiner Text eingefügt und als neuer Eintrag im Verlauf abgelegt. Das Original bleibt unverändert. Ohne Änderung wird der Eintrag wie sonst eingefügt, also mit Formatierung, wenn das der Standard ist.
- **Zurück:** Esc oder der Knopf „Zurück“.

**Sensible Einträge** bleiben in der Vorschau zensiert und schreibgeschützt, bis Sie „Anzeigen“ drücken. „Verbergen“ stellt die Zensur wieder her.

**Grenzen.** Texte über 200.000 Zeichen zeigt die Vorschau nur zum Anfang und nicht bearbeitbar; eingefügt wird dann das Original. Ein Rückgängig-Befehl ist im Editor nicht eingebaut.

## Formatierung beim Einfügen

SuperV speichert Formatierung mit, und standardmäßig fügen Enter und Klick nur den reinen Text ein. Ein Zusatzknopf liefert die Formatierung mit.

Wurde etwas mit Formatierung kopiert (fett, Links, Listen, etwa aus einer Webseite oder einem Office-Dokument), steht beim Eintrag „formatiert“. Links neben der Pinnnadel erscheint dann ein Knopf mit einem unterstrichenen A. Nur solche Einträge haben ihn; Bilder und reiner Text nicht.

| Einstellung „Standardmäßig mit Formatierung einfügen“ | Enter und Klick | Knopf neben der Pinnnadel | Umschalt+Enter |
| --- | --- | --- | --- |
| aus (Standard) | ohne Formatierung | mit Formatierung | mit Formatierung |
| an | mit Formatierung | ohne Formatierung | ohne Formatierung |

Beim Einfügen mit Formatierung bietet SuperV der Zielanwendung beide Formen gleichzeitig an, HTML und reinen Text. Welche davon übernommen wird, entscheidet das Zielprogramm: Textverarbeitungen und Browser können die Formatierung übernehmen, Terminals zeigen nur den Text.

Bei zu großen Kopien (HTML über 300.000 Zeichen) speichert SuperV nur den reinen Text. Aus Einträgen ohne Formatierung wird auch mit dem Knopf nichts Formatiertes.

## Fensterposition und Monitore

Das Fenster öffnet sich mittig auf dem Monitor, auf dem Sie arbeiten, und wenn Sie es verschieben, merkt sich SuperV die Stelle für genau diesen Monitor.

- **Welcher Monitor?** Unter X11 der Monitor des aktiven Fensters, ersatzweise der des Mauszeigers. Unter Wayland der Monitor des Mauszeigers: Ein unsichtbares Hilfsfenster fragt den Desktop, wo er neue Fenster platziert, danach erscheint das Fenster einmal an seinem Platz.
- **Verschieben:** Kopfzeile oder Fußzeile mit der Maus ziehen. Die Stelle wird pro Monitor in `state.json` gespeichert, relativ zur Ecke des Monitors.
- **Beim nächsten Öffnen** nutzt SuperV für den aktuellen Monitor die gemerkte Stelle. Monitore, auf denen Sie nie verschoben haben, bleiben mittig. Liegt die gemerkte Stelle außerhalb des Monitors, wird sie in den sichtbaren Bereich zurückgesetzt.
- **Monitorwechsel:** Ein Monitor wird an Hersteller, Modell, Auflösung und Lage erkannt. Ändern Sie die Anordnung der Bildschirme, gilt er als neuer Monitor.
- **Zurücksetzen:** In den Einstellungen „Gemerkte Positionen vergessen“, oder die Funktion mit „Fensterposition pro Monitor merken“ ausschalten.

Die Einstellung `position` in der Datei `config.json` kennt `auto` (Standard, mittig) und `pointer` (unter X11 an der Stelle des Mauszeigers). Eine gemerkte Position hat in beiden Fällen Vorrang.

## Einstellungen

Die wichtigsten Einstellungen stehen im Einstellungsfenster (Zahnrad im Kopf des Fensters); alle zusammen in `~/.config/superv/config.json`. Das Fenster ändert erst etwas, wenn Sie „Speichern“ drücken. „Abbrechen“ oder Esc verwirft die Änderungen.

| Schlüssel in config.json | Standard | Bedeutung und Einstellungsfenster |
| --- | --- | --- |
| `max_items` | 50 | Zahl der nicht angehefteten Einträge, 1 bis 500. Fenster: „Einträge im Verlauf“ (5 bis 500) |
| `expire_days` | 30 | Nicht angeheftete Einträge, die älter sind, werden gelöscht; 0 = nie, höchstens 3650. Fenster: „Einträge löschen nach (Tagen)“ |
| `remember_position` | true | Fensterposition pro Monitor merken. Fenster: „Fensterposition pro Monitor merken“ |
| `paste_on_select` | true | Beim Auswählen sofort einfügen; aus = Eintrag wird nur in die Zwischenablage gelegt. Fenster: „Beim Auswählen sofort einfügen“ |
| `paste_shortcut` | `shift+insert` | Taste, die SuperV zum Einfügen sendet: `shift+insert`, `ctrl+v` oder `ctrl+shift+v`. Fenster: „Tastenkürzel zum Einfügen“ |
| `paste_formatted` | false | Standardmäßig mit Formatierung einfügen. Fenster: „Standardmäßig mit Formatierung einfügen“ |
| `persist` | true | Verlauf nach dem Abmelden behalten. Fenster: „Verlauf nach dem Abmelden behalten“ |
| `position` | `auto` | `auto` = mittig auf dem Monitor, `pointer` = am Mauszeiger (nur X11); nur in der Datei |
| `max_text_chars` | 1000000 | längere Texte werden nicht aufgenommen; nur in der Datei |
| `max_image_pixels` | 40000000 | Bilder mit mehr Pixeln (Breite mal Höhe) werden nicht aufgenommen; nur in der Datei |
| `max_html_chars` | 300000 | größere Formatierung wird verworfen, der Text bleibt; nur in der Datei |

**Gut zu wissen.**

- Das Einfügen mit `shift+insert` (Standard) funktioniert auch in Terminals. Dafür setzt SuperV zusätzlich die Maus-Auswahl (primary selection) auf den reinen Text.
- Beim Speichern im Fenster werden zu viele oder zu alte Einträge sofort gelöscht. Das Alter prüft SuperV außerdem beim Start, beim Öffnen des Fensters und stündlich.
- Haben Sie `config.json` von Hand geändert, starten Sie neu: `superv --quit; superv &`. Fehlt die Datei, legt SuperV sie beim Start mit den Standardwerten an.

## Dateien, Speicherort und Datenschutz

SuperV speichert alles lokal in Ihrem Home-Verzeichnis und baut keine Netzwerkverbindung auf. Die Ordner sind nur für Sie lesbar (Rechte 700), die Dateien ebenfalls (600).

| Pfad | Inhalt |
| --- | --- |
| `~/.local/share/superv/history.json` | der Verlauf: Text, gegebenenfalls Formatierung (HTML), Anheft-Status, Zeitpunkt; sensible Texte unzensiert |
| `~/.local/share/superv/images/` | kopierte Bilder als PNG |
| `~/.config/superv/config.json` | Einstellungen |
| `~/.config/superv/state.json` | gemerkte Fensterpositionen pro Monitor |
| `~/.config/superv/hotkey-installed` | Markierung, dass das Tastenkürzel schon eingetragen wurde |

**Was nicht aufgezeichnet wird.**

- Kopien, die ein Passwortmanager mit dem Hinweis „vertraulich“ (`x-kde-passwordManagerHint`) kennzeichnet. KeePassXC tut das; ob ein anderer Manager es tut, hängt von diesem ab.
- Leere oder nur aus Leerzeichen bestehende Texte.
- Texte über 1.000.000 Zeichen und Bilder über 40 Millionen Pixel (einstellbar in `config.json`).

**Verlauf löschen.** „Alle löschen“ entfernt alles außer angehefteten Einträgen. Zum vollständigen Löschen `superv --quit` ausführen und `~/.local/share/superv` entfernen. Wer den Verlauf nicht auf der Festplatte haben will, stellt „Verlauf nach dem Abmelden behalten“ aus; dann schreibt SuperV keine history.json. Kopierte Bilder liegen im Betrieb trotzdem im Ordner images und werden beim nächsten Start gelöscht.

## Befehle

Alle Befehle laufen über das Programm `superv` und sprechen den schon laufenden Hintergrundprozess an.

| Befehl | Wirkung |
| --- | --- |
| `superv` | Hintergrundprozess starten (macht das Autostart-Eintrag beim Login), ohne das Fenster zu zeigen |
| `superv --show` (`-s`) | Fenster zeigen; startet den Prozess, falls er nicht läuft |
| `superv --toggle` (`-t`) | Fenster zeigen oder verbergen |
| `superv --quit` (`-q`) | Hintergrundprozess beenden und den Verlauf speichern |
| `superv --setup-hotkey` | Super+V (neu) als Tastenkürzel eintragen |
| `superv --remove-hotkey` | Tastenkürzel entfernen und Super+V an GNOME zurückgeben |
| `superv --version` (`-v`) | Version ausgeben |
| `superv-toggle` | wird vom Tastenkürzel aufgerufen; schaltet das Fenster über D-Bus um und startet SuperV, falls es nicht läuft |

## So funktioniert es

Ein kleiner Hintergrundprozess beobachtet die Zwischenablage, das Fenster ist nur seine Anzeige. Der Weg eines Eintrags:

1. Sie kopieren etwas. Der Prozess merkt den Besitzerwechsel der Zwischenablage und liest, welche Formate angeboten werden.
2. Trägt die Kopie den Passwortmanager-Hinweis, wird sie verworfen. Sonst liest SuperV Text (und, falls vorhanden, `text/html`) oder ein Bild.
3. Text wird einsortiert (Sensibel, URLs, Code, Text) und gespeichert. Derselbe Text wird nicht doppelt abgelegt, sondern nach vorn geholt, mit neuer Zeit.
4. Super+V ruft `superv-toggle` auf, das das Fenster per D-Bus öffnet. Das Fenster zeigt den Verlauf.
5. Bei Auswahl legt SuperV den Eintrag in die Zwischenablage, schließt das Fenster und sendet nach etwa 0,2 Sekunden die Einfügetaste über eine virtuelle Tastatur.

**Bausteine und Gründe.**

- **X11 auch unter Wayland.** Der Prozess läuft als X11-Programm (über XWayland), weil unter GNOME-Wayland nur solche Programme erfahren, was in anderen Fenstern kopiert wird.
- **Virtuelle Tastatur.** Das Einfügen läuft über `/dev/uinput`, weil Wayland kein Tastendrücken in fremde Fenster erlaubt. Nur unter X11 gibt es als Ersatz `xdotool`.
- **Formatierung.** Ein unsichtbares Widget übernimmt die Zwischenablage und beantwortet Anfragen sowohl mit HTML als auch mit reinem Text.
- **Fenster ohne Aufflackern.** Es wird erst sichtbar, wenn es an seinem Platz steht; unter Wayland ermittelt vorher ein unsichtbares 1×1-Fenster den Monitor.
- **Tastenkürzel.** Als benutzerdefiniertes GNOME-Kürzel eingetragen, das `superv-toggle` startet.
- **Metadaten für Software-Center.** Das Paket enthält AppStream-Daten (Name „SuperV“, Entwickler, Versionsnotizen).

## Grenzen und bekannte Einschränkungen

SuperV ist ein kleines Werkzeug, und einige Dinge kann es bewusst oder technisch nicht.

- **Dateien.** Kopierte Dateien speichert SuperV nicht als Dateien; je nach Dateimanager erscheint höchstens ihr Pfad als Text.
- **Formatierung.** Es wird nur HTML gespeichert, kein RTF. Ob die Zielanwendung die Formatierung übernimmt, entscheidet sie selbst.
- **Erkennung sensibler Daten.** Sie beruht auf Mustern und liegt manchmal falsch. Eine manuelle Umsortierung gibt es nicht. Die Zensur schützt nur die Anzeige, nicht die Datei und nicht die Suche.
- **Passwortmanager.** Nur Kopien mit Vertraulichkeits-Hinweis werden übersprungen. Ohne Hinweis zeichnet SuperV das Kopierte auf.
- **Einfügen ohne /dev/uinput.** Unter Wayland kann SuperV dann keine Taste senden. Der Eintrag liegt in der Zwischenablage, und im Fußtext des Fensters steht, dass Sie selbst mit Strg+V einfügen. Unter X11 hilft `xdotool`.
- **Fenster unter Wayland.** Es erscheint mittig auf dem Monitor mit dem Mauszeiger; das Platzieren am Mauszeiger gibt es nur unter X11. Ob das Fenster beim Öffnen sofort den Tastaturfokus bekommt, entscheidet der Desktop.
- **Monitore.** Ändern Sie die Anordnung der Bildschirme, beginnt SuperV für den so veränderten Monitor wieder mittig; die alte Position ist dann nicht mehr zugeordnet.
- **Editor.** Die Vorschau hat kein Rückgängig; Texte über 200.000 Zeichen sind dort nicht bearbeitbar.
- **Software-Center.** Öffnen Sie die .deb-Datei in der Software-App, steht dort der Paketname `superv` (Debian erlaubt keine Großbuchstaben). Nach der Installation heißt die Anwendung „SuperV“.

## Fehlerbehebung

Die meisten Probleme betreffen das Tastenkürzel oder das Einfügen. Meldungen des Programms erscheinen im Terminal, wenn Sie es dort starten: `superv --quit; superv`.

| Problem | Ursache und Lösung |
| --- | --- |
| Super+V tut nichts | `superv --setup-hotkey` ausführen. Prüfen, ob der Prozess läuft (`pgrep -af superv`) und ob unter Einstellungen > Tastatur ein anderes Kürzel Super+V belegt. |
| Fenster öffnet, aber Einfügen passiert nicht | Steht im Fußtext „Enter kopiert den Eintrag – danach mit Strg+V einfügen“, fehlt der Zugriff auf `/dev/uinput`. Einmal ab- und anmelden; `ls -l /dev/uinput` zeigt, ob die Berechtigung gesetzt ist. Unter X11 hilft `sudo apt install xdotool`. |
| In einem Terminal kommt nichts oder das Falsche an | Standard ist `shift+insert`. Falls das Programm eine andere Taste braucht, in den Einstellungen „Tastenkürzel zum Einfügen“ auf `ctrl+shift+v` stellen. |
| Fenster erscheint auf dem falschen Monitor | In den Einstellungen „Gemerkte Positionen vergessen“. Unter Wayland entscheidet der Mauszeiger, unter X11 das aktive Fenster. |
| Eintrag ist fälschlich sensibel oder nicht sensibel | Das liegt an der Mustererkennung. Löschen und neu Kopieren ändert nichts, denn der Text wird wieder genauso einsortiert; eine Korrektur pro Eintrag ist nicht vorgesehen. |
| Verlauf ist nach dem Anmelden leer | Prüfen, ob „Verlauf nach dem Abmelden behalten“ aktiv ist und ob `expire_days` die Einträge schon gelöscht hat. |
| Die Software-App zeigt eine alte Version oder den Namen `superv` | Für die installierte Anwendung `gnome-software --quit` ausführen und die App neu öffnen; notfalls ab- und anmelden. Für eine geöffnete .deb-Datei siehe „Grenzen“. |

## Update und Deinstallation

Ein Update ersetzt nur das Programm; Verlauf und Einstellungen bleiben erhalten.

**Update.** Die neue .deb-Datei mit demselben Befehl installieren. Die Installation beendet den laufenden Prozess; der nächste Druck auf Super+V oder das nächste Login startet die neue Version.

```
sudo apt install ./superv_<Version>_all.deb
superv --quit; superv --show
```

**Deinstallation.**

```
superv --remove-hotkey
sudo apt remove superv
rm -rf ~/.config/superv ~/.local/share/superv
```

Der erste Befehl gibt Super+V an GNOME zurück. Die letzte Zeile löscht Verlauf und Einstellungen; ohne sie bleiben beide für eine spätere Neuinstallation liegen.

## Aus dem Quellcode bauen

Das Quellarchiv baut mit einem einzigen Skript ein .deb; neben den Standardwerkzeugen braucht es nur `dpkg-deb`.

```
tar xzf superv-1.2.0-source.tar.gz
cd superv
./build.sh
```

Das Ergebnis liegt unter `build/superv_<Version>_all.deb`. Die Version liest das Skript aus der Zeile `VERSION = "…"` in `src/superv`.

| Ordner oder Datei | Inhalt |
| --- | --- |
| `src/superv` | das Programm (eine Python-Datei) |
| `src/superv-toggle` | kleines Skript, das das Tastenkürzel aufruft |
| `data/` | Desktop-Einträge, Symbole, udev-Regel, AppStream-Dateien, README |
| `debian/` | Paketdaten: `control.in`, `postinst`, `prerm`, `postrm`, `changelog`, `copyright` |
| `build.sh` | baut das Paket |

**Neue Version veröffentlichen.**

1. `VERSION` in `src/superv` erhöhen.
2. Oben in `debian/changelog` einen neuen Eintrag anlegen.
3. In `data/org.superv.Clipboard.metainfo.xml` und `data/org.superv.Clipboard.catalog.xml` einen neuen `<release>`-Eintrag ergänzen. Der oberste trägt `@VERSION@`; der bisher oberste bekommt seine feste Versionsnummer.
4. `./build.sh` ausführen.

## Versionsverlauf

| Version | Datum | Änderungen |
| --- | --- | --- |
| 1.2.0 | 16.11.2026 | Vorschau mit Bearbeiten (Leertaste); Einfügen mit oder ohne Formatierung, Knopf neben der Pinnnadel und Einstellung; Versionsnotizen für das Software-Center |
| 1.1.1 | 16.11.2026 | Fenster blitzt nicht mehr vor dem Platzieren auf; Strg+Zahl wartet auf das Loslassen von Strg; Reiter „URLs“; Namen wie `Mobile_pos2` gelten nicht mehr als Passwort |
| 1.1.0 | 16.11.2026 | Schnellwahl mit Strg+1 bis 9; Zeitangabe je Eintrag; Position pro Monitor merken; automatisches Löschen; Reiter Text, Code, Sensibel, Bilder mit Zensur; Einstellungsfenster |
| 1.0.7 | 13.11.2026 | Versionsnummer mittig im Fensterkopf |
| 1.0.6 | 13.11.2026 | Versionsnummer statt Autor im Fensterkopf |
| 1.0.5 | 13.11.2026 | AppStream-Katalogdaten für den Namen „SuperV“; Greifer-Mauszeiger entfernt |
| 1.0.4 | 13.11.2026 | Paketbeschreibung mit Name und Autor |
| 1.0.3 | 13.11.2026 | Fenster per Maus verschiebbar; AppStream-Metadaten |
| 1.0.2 | 13.11.2026 | Autorenangabe |
| 1.0.1 | 13.11.2026 | Darstellung der markierten Zeile korrigiert; Öffnen auf dem aktuellen Monitor |
| 1.0.0 | 13.11.2026 | erste Version: Verlauf für Text und Bilder, Super+V, Suche, Anheften |
