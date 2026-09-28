---
title: Bob der Job-Bot | Tjark Dreyer
description: Bob der Job-Bot: Mehrnutzer-Job-Scanner als Web-App mit MCP-Server, live in Betrieb.
---

## bob.main.1
← Zurück zu den Projekten

## bob.main.2
Bob ist ein Job-Scanner für mehrere Nutzer. Alle Funde landen in einem gemeinsamen Pool. Bewertet
wird für jedes Profil getrennt. Der Dienst läuft live mit echten Mitnutzern.

## bob.main.3
Die Idee

## bob.main.4
Wer einen Job sucht, durchsucht dieselben Portale wie alle anderen. Jeder sucht für sich und jeden
Tag neu. Die meisten Anzeigen verwirft man dabei wieder. Die Frage hinter Bob war: Warum sucht
eigentlich jeder einzeln?

## bob.main.5
Bob dreht das um. Alle Funde landen in einem gemeinsamen Pool. Bewertet wird aber pro Profil. Nicht
jeder interessante Job ist für einen selbst der richtige. Für jemand anderen ist er vielleicht der
Traumjob. Eine Anzeige, die ich verwerfe, ist damit nicht verloren. Sie taucht bei dem Mitglied auf,
zu dessen Profil sie passt.

## bob.main.6
Worum es geht

## bob.main.7
Bob sammelt Stellenanzeigen von mehreren Jobportalen in einem gemeinsamen Pool. Jede Anzeige
bewertet er gegen die Kriterien des jeweiligen Profils. Das Ergebnis zeigt eine Web-App mit
In-App-Inbox. Darunter liegt eine FastAPI-Anwendung mit SQLite als Datenhaltung. Ein MCP-Server in
derselben App macht denselben Datenbestand direkt aus Claude Code heraus ansprechbar. Der Zugriff
ist dabei pro Nutzer begrenzt.

## bob.main.8
Bob läuft als geschlossene Alpha mit Kommilitonen. Rückmeldungen kommen über ein Feedback-Widget
direkt aus der App. Wichtig war mir Transparenz. Der Quellcode ist öffentlich. Das Member-Kit für
den Scan nutzt ausschließlich das eigene Claude-Abo des jeweiligen Mitglieds. API-Kosten fallen
dadurch keine an.

## bob.main.9
Zum Projekt gehören Scraping, Datenmodell, Scoring, Web-Oberfläche, MCP-Server und der Betrieb auf
einem eigenen Server. Bob war mein erstes großes Projekt außerhalb der Engine. Es war auch das
erste, das ich durchgehend mit meinem eigenen Harness und selbst gebauten Skills entwickelt habe.
Die KI schreibt mit. Die Architektur, die Sicherheitsfragen und der Betrieb liegen bei mir.

## bob.main.10
Bewertet wird zuerst nach festen Regeln und erst im Zweifel mit einem LLM. Gescannt wird nicht vom
Server. Das übernehmen die Mitglieder über die eigene Leitung. Ein Sicherheitsaudit und über 1200
Tests sichern den Dienst ab.

## bob.main.11
Highlights & Herausforderungen

## bob.main.12
Regeln entscheiden zuerst

## bob.main.13
Die Bewertung beginnt deterministisch. Eine Regel-Engine mit 25 gewichteten Kriterien und 25 harten
No-Go-Vetos bewertet jede Anzeige ohne LLM. Das LLM läuft nur auf dem „Vielleicht“-Band. Dort können
die Regeln allein nicht entscheiden. Rückmeldungen per Daumen hoch oder Daumen runter passen die
Gewichte an.

## bob.main.14
Geteilt wird ausdrücklich nur der Job-Pool. Kriterien, Bewertungen und Erkenntnisse bleiben strikt
pro Profil. Dieselbe Anzeige kann für zwei Mitglieder völlig unterschiedlich bewertet werden. Die
Bewertungen vermischen sich dabei nie.

## bob.main.15
Die Hürde war die IP und nicht der Browser

## bob.main.16
Das Sammeln ist der unzuverlässigste Teil des Systems. Portale ändern ihr Markup, drosseln Zugriffe
und erkennen automatisierte Abrufe. Lange sah es nach einem Problem der Browser-Tarnung aus. Dann
hat ein Live-Test diese Annahme widerlegt und den eigentlichen Grund gezeigt.

## bob.main.17
Der entscheidende Schritt beim Scraping war kein Trick, sondern eine Diagnose. Die Portale blocken
Rechenzentrums-IPs. Das Problem war also nicht der Browser-Fingerabdruck. Es war die Reputation der
Server-IP. Vom Rechenzentrum aus ging es nicht. Von einem Wohnanschluss aus schon.

## bob.main.18
Daraus wurde die Architektur. Gescannt wird nicht automatisch vom Server. Die Mitglieder scannen
selbst per Befehl im eigenen Claude Code und über die eigene Leitung von zu Hause aus. Die Funde
landen über den MCP-Server im gemeinsamen Pool. Der Server ergänzt Aggregatoren wie Adzuna und
Jooble mit den Zugangsschlüsseln der jeweiligen Mitglieder. Diese Erfahrung hat meine Arbeitsweise
verändert. Eine Theorie prüfe ich heute zuerst mit dem kleinstmöglichen echten Test. Erst danach
baue ich darauf weiter.

## bob.main.19
Sicherheit an fremden Zugängen

## bob.main.20
Damit sind fremde Inhalte und fremde Zugänge im Spiel. Deshalb liegt viel Arbeit in Sicherheit und
Verlässlichkeit. Dazu gehören ein Token pro Mitglied, ein pro Nutzer begrenzter Datenzugriff und der
Schutz gegen Prompt-Injection an der MCP-Grenze. Hinzu kommen die Absicherung gegen CSRF und SSRF
sowie eine gehärtete SQLite-Schicht. Ein Sicherheitsaudit ergab fünf Befunde. Darunter war eine
Cross-Tenant-Lücke der Stufe HIGH. Alle fünf sind behoben. Jede Korrektur ist mit einem eigenen Test
abgesichert.

## bob.main.21
Betrieb für andere

## bob.main.22
Der zweite harte Teil war, dass Bob nicht nur für mich läuft. Sobald andere mitmachen, erleben sie
jede Fehlerquelle selbst. Drei Beispiele: Ein Login funktioniert nur bei mir. Ein Mailversand
scheitert ohne korrekte Domain-Einträge stillschweigend. Eine Testsuite ist grün und die Seite
liefert live noch alte Dateien aus. Hier hat es sich zum ersten Mal über Wochen im Betrieb bewährt,
Entscheidungen und Erkenntnisse systematisch festzuhalten. So passiert derselbe Fehler nicht
zweimal.

## bob.main.23
Das Projekt zeigt vor allem, dass ich mich eigenständig in einen fremden Stack einarbeite. Ich
bringe ihn nicht nur zum Laufen. Ich halte ihn auch am Laufen. Fehler nach Wochen im Betrieb sind
eine andere Kategorie als Fehler in einer Abgabe. Betrieb heißt hier konkret: tägliches
SQLite-Backup, Healthcheck mit Alarm und Patch-Releases nach SemVer. Dazu kommen über 1200 Tests.
Sie sichern ab, dass eine Korrektur nichts anderes kaputt macht.

## bob.main.24
Offen: die Trefferquote

## bob.main.25
Offen ist die Trefferquote. Sie fällt je Portal unterschiedlich aus. Ein Browser-Scan liefert heute
deutlich mehr Anzeigen als brauchbare Treffer. Das Erkennen abgelaufener Anzeigen ist genauso mühsam
wie das Einsammeln. Beides steht dokumentiert auf der Liste.

## bob.main.26
Roadmap

## bob.main.27
Als Nächstes steht die Bewerbungserstellung an. Anschreiben und Lebenslauf entstehen dann aus den
Job- und Firmendaten einer Anzeige. Danach folgen ein Bewerbungs-Tracking, eine Mobile-App und
Gamification-Elemente.

## bob.main.28
Code ansehen

## bob.detail-next.1
Nächstes Projekt: Desk-Buddy

## bob.detail-next.2
Kontakt
