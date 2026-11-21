# Budget-Freigabe nach Betrag

Die Höhe eines Antrags bestimmt, wer zustimmen muss. Ist jemand abwesend, übernimmt die
hinterlegte Vertretung. Niemand gibt den eigenen Antrag frei, niemand zeichnet zweimal, und
jeder Schritt steht im Protokoll. Dazu eine Freigabe per Anruf.

Showroom ADH, Tool vom 21.11.2026. Firma, Personen und Anträge sind erfunden.

| | |
|---|---|
| Landingpage | https://adh-gh.github.io/budget-freigabe/ |
| Live-Tool | https://adh-gh.github.io/budget-freigabe/app/ |
| Produktvideo | https://adh-gh.github.io/budget-freigabe/demo.mp4 |

## Stand

| Teil | Stand |
|---|---|
| Freigabeweg nach drei Betragsgrenzen, vier Stufen | läuft, getestet |
| Vier-Augen-Regel: eigene Stufe entfällt, niemand zeichnet zweimal | läuft, getestet |
| Abwesenheit und Vertretung, Sperre bei beteiligter Vertretung | läuft, getestet |
| Protokoll und Kennzahlen | läuft, lebt nur im Browserfenster |
| Freigabe per Anruf im Browser (ElevenLabs) | Werkzeuge getestet, Gespräch getippt geprüft, mit Mikrofon ungeprüft |
| Anruf auf das Telefon | nicht gebaut |
| Ablauf auf einem Server, Anmeldung, Anschluss an Odoo, SAP, DATEV oder Microsoft 365 | nicht gebaut |

## Ausprobieren

`docs/app/index.html` per Doppelklick öffnen. Kein Build, kein Server, keine Installation.

1. Neuer Antrag: Lena Hartmann, Kostenstelle 4100, „Hubwagen elektrisch“, Betrag `8400`. Die
   Vorschau zeigt zwei Zustimmungen.
2. „Angemeldet als“ Jonas Weber, im Eingang freigeben. Der Antrag wartet jetzt auf Hanna Vogt.
3. Bei „Rollen und Vertretung“ Hanna Vogt abwesend setzen. Carsten Brandt vertritt sie und gibt frei.
4. Im Protokoll steht jeder Schritt, auch die Abwesenheit.

## Freigabe per Anruf

Im Eingang startet „Anruf annehmen“ ein Gespräch mit einem ElevenLabs-Agenten, wahlweise
getippt über „Stattdessen schreiben“. Der Assistent liest vor, was auf die gewählte Person
wartet, wiederholt jede Entscheidung und führt sie erst nach einem klaren Ja aus.

Der Agent spricht nur. Was er tut, läuft über drei Werkzeuge in der Seite
(`offene_freigaben`, `freigeben`, `ablehnen`), und die prüfen dieselben Regeln wie die Knöpfe.
Er kann also nichts freigeben, was die Person am Telefon nicht selbst freigeben dürfte.

Den Agenten anlegen oder ändern:

```bash
ELEVENLABS_API_KEY=... python3 voice/agent_anlegen.py
```

Die Kennung steht danach in `voice/agent.json` und muss in `docs/app/index.html` als
`AGENT_ID` stehen. Der Agent ist öffentlich erreichbar, deshalb auf 40 Gespräche am Tag und
fünf Minuten je Gespräch begrenzt.

**Was der Anruf nicht ist:** kein Anruf auf ein Telefon. Dafür muss der Stand der Anträge auf
einem Server liegen, und es braucht eine Rufnummer. Beides gehört zur Einführung.

## Tests

```bash
node --test tests/regeln.test.mjs
```

Die Tests laden das Skript der Seite ohne Browser und prüfen den Freigabeweg, die
Vier-Augen-Regel, die Vertretung mit Sperre und die drei Werkzeuge des Anrufs.

## Aufbau

```
docs/index.html        Landingpage
docs/app/index.html    das Tool, eine Datei
docs/demo.mp4          Produktvideo
voice/agent_anlegen.py legt den ElevenLabs-Agenten an
tests/                 Regeltests
```

## Von der Vorführung zur Einführung

1. **Regelung aufnehmen.** Betragsgrenzen, Rollen, Vertretungen und Sonderfälle aus der
   bestehenden Unterschriftenregelung.
2. **Ablauf auf den Server.** Dieselben Regeln mit Datenbank für Anträge und Protokoll,
   Anmeldung über das vorhandene Konto.
3. **Anschluss an ein System.** Odoo, SAP, DATEV oder Microsoft 365.
4. **Pilot in einem Bereich**, vier Wochen, dann die Ausweitung.

Wer Freigaben in SAP, Odoo Enterprise oder Teams schon eingerichtet hat und nutzt, braucht
das nicht. Gedacht ist es für Unternehmen, in denen Freigaben heute über Mail und Zuruf laufen.

## Was die Seite nicht kennt

Zwei Personen derselben Stufe gleichzeitig, Prüfung gegen das Jahresbudget, Teilfreigabe,
Rückfrage statt Ablehnung, Erinnerung und Eskalation nach Frist, Anträge über mehrere
Kostenstellen, eine Ersatzvertretung, wenn die Vertretung gesperrt ist.

## Rechte

Alle Rechte vorbehalten, Alf-David Heermann 2026. Der Quelltext ist zum Ansehen und Ausprobieren
veröffentlicht. Kontakt: https://www.linkedin.com/in/alf-david-heermann
