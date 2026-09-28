---
title: Desk-Buddy | Tjark Dreyer
description: Desk-Buddy: transparentes Desktop-Pet in Unity. Je länger du sitzt, desto krummer sitzt die Figur. Windows-Prototyp.
---

## desk-buddy.main.1
← Zurück zu den Projekten

## desk-buddy.main.2
in Arbeit

## desk-buddy.main.3
Der Desk-Buddy ist ein Desktop-Pet für Windows. Je länger man sitzt, desto krummer sitzt die Figur.
Eine kurze Übung richtet sie wieder auf. Der Stand ist ein Prototyp.

## desk-buddy.main.4
Die Idee

## desk-buddy.main.5
Die Idee kommt direkt aus der Sportwissenschaft. Bewegungspausen wirken, wenn sie zur Gewohnheit
werden. Gewohnheiten entstehen über Motivation und Rückmeldung und nicht über Mahnungen.

## desk-buddy.main.6
Der Desk-Buddy erinnert deshalb nicht wie ein Timer. Er sitzt mit am Schreibtisch und ihm fällt auf,
wenn man zu lange sitzt. Das Vorbild ist die Tamagotchi-Mechanik und nicht das Timer-Popup. So ist
daraus keine Benachrichtigung geworden. Entstanden ist eine Figur, um deren Haltung man sich
kümmert.

## desk-buddy.main.7
Worum es geht

## desk-buddy.main.8
Der Desk-Buddy ist ein transparentes Desktop-Pet in Unity. Er läuft über dem Windows-Desktop. Die
Haltung der Figur verfällt in Stufen mit der eigenen Sitzzeit. Es gibt kein Popup und keinen Ton.
Die Figur nimmt auch den Fokus nicht weg. Wann man darauf reagiert, entscheidet man selbst.

## desk-buddy.main.9
Der Kernablauf läuft als Windows-Build. Ein Klick auf die Figur öffnet die Auswahl eines
Zeitfensters. Zur Wahl stehen 30 Sekunden, 2, 5 oder 15 Minuten. Daraus entsteht ein Übungsplan aus
einer Datenbank mit 28 Übungen. Die Figur macht jede Übung mit Intro, Loop und Outro vor. Ihre
Haltung erholt sich dabei.

## desk-buddy.main.10
Der Desk-Buddy ist in Arbeit und hat bewusst keinen Repo-Link. Der Stand ist ein Prototyp. Der Code
hängt an Dingen, die ich nicht veröffentlichen darf. Final IK ist ein gekauftes Asset. Das
SMPL-X-Körpermodell der Mocap-Kette steht unter einer Non-Commercial-Research-Lizenz. Entwickelt
habe ich den Desk-Buddy zusammen mit KI. Die Idee, der Aufbau und die Motion-Capture-Pipeline sind
meine Entscheidungen.

## desk-buddy.main.11
Das Overlay ist eine eigene Schicht auf der Fensterebene von Windows. Das Belastungsmodell rechnet
einen simulierten Arbeitstag in Millisekunden durch. Für die Übungsclips ist eine lokale
Motion-Capture-Kette entstanden. Sie arbeitet mit selbst gedrehten Videos.

## desk-buddy.main.12
Highlights & Herausforderungen

## desk-buddy.main.13
Ein Overlay ohne Hilfe der Engine

## desk-buddy.main.14
Unity ist nicht für Desktop-Overlays gedacht. Ein rahmenloses Fenster mit transparentem Hintergrund
und dauerhaft im Vordergrund ist kein Engine-Feature. Es ist Arbeit an der Fensterebene des
Betriebssystems.

## desk-buddy.main.15
Das Overlay ist deshalb eine eigene Win32-Interop-Schicht. Die 3D-Figur wird direkt in den
Backbuffer eines randlosen und transparenten Fensters gerendert. Ein Topmost-Re-Assert hält das
Fenster im Vordergrund. Dazu kommt ein Click-through-Zustandsautomat mit Drag-Lock. Ihn habe ich
test-first gebaut. Damit ist die erste Hürde überwunden.

## desk-buddy.main.16
Ein Arbeitstag in Millisekunden

## desk-buddy.main.17
Das Belastungsmodell hinter der Figur ist Unity-frei und bekommt seine Uhr injiziert. Dadurch läuft
ein simulierter Arbeitstag im EditMode in Millisekunden durch und nicht in Echtzeit. EditMode-Tests
sichern die Logik ab. Der Zustand wird gespeichert und übersteht einen Neustart.

## desk-buddy.main.18
Eine lokale Motion-Capture-Kette

## desk-buddy.main.19
Das größere Stück ist die Motion-Capture-Kette, die dabei entstanden ist. Sie läuft komplett lokal:
selbst gedrehtes Video → GVHMR unter WSL2 → Blender headless → FBX → Unity. Die Bereinigung läuft
über Final IK. Im A/B-Vergleich am selben Clip schlug die lokale Kette den Bezahldienst. Inzwischen
ist die Pipeline ein eigenes Projekt und als Package ausgelagert.

## desk-buddy.main.20
Die zweite Hürde war die Pipeline selbst. Aufnahme, Bereinigung und Backen mussten so weit kommen,
dass am Ende ein sauberer Loop steht. Grounding und Jitter-Dämpfung gehören dazu. Sonst schwebt oder
zittert die Figur. Fertig ist das nicht. Stehende Übungen sind noch ungetestet.

## desk-buddy.main.21
Was noch offen ist

## desk-buddy.main.22
Offen ist vor allem die Produktion der 28 Übungsclips. Bisher läuft alles mit Platzhalter-Clips.
Dazu kommen weitere Haltungs-Idles. Sechs sind geplant. Auch Alltagstauglichkeit wie Autostart und
Multi-Monitor fehlt noch. Genau deshalb spreche ich von einem Prototyp und nicht von einem fertigen
Produkt.

## desk-buddy.detail-next.1
Nächstes Projekt: Izzy's Island Party

## desk-buddy.detail-next.2
Kontakt
