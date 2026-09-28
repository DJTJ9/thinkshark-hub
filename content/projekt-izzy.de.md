---
title: Izzy's Island Party | Tjark Dreyer
description: Izzy's Island Party: lokale Party-Minispiel-Sammlung in Unity, SAE-Abschlussprojekt im 2er-Team.
---

## izzy.main.1
← Zurück zu den Projekten

## izzy.main.2
Izzy’s Island Party ist eine Sammlung aus sechs Minispielen für ein bis vier Spieler. Sie ist mein
Abschlussprojekt im Studiengang Games Programming am SAE Institute Hamburg. Gebaut haben wir sie im
Zweierteam in Unity 6 von November 2025 bis März 2026.

## izzy.main.3
Die Idee

## izzy.main.4
Die Grundidee war eine Sammlung witziger Minispiele, die man auch auf einer Party spielen kann.
Deshalb spielt man lokal gegeneinander. Freie Plätze übernehmen Computergegner. Gespielt wird mit
Controller oder Tastatur.

## izzy.main.5
Die Minispiele waren klar aufgeteilt. Drei lagen bei mir und drei bei meiner Projektpartnerin. Meine
drei sind Minigolf Mayhem, Swaggy Snapshots und Bowling Battle. Ich habe sie eigenständig gebaut,
von der Spielmechanik bis zu den Computergegnern. Design und Ideen haben wir laufend miteinander
abgestimmt.

## izzy.main.6
Dieses Projekt ist ohne Coding-Agents und ohne andere KI-Hilfe entstanden. Den Code meiner drei
Spiele habe ich selbst geschrieben. Es zeigt damit am deutlichsten, was ich in einem laufenden
Teamprojekt allein bis in den spielbaren Zustand bringe. Dabei halte ich mich an gemeinsame
Schnittstellen und biege sie mir nicht zurecht.

## izzy.main.7
Die gemeinsame Basis

## izzy.main.8
Spielrahmen, Menü, Spielerverwaltung und die Integration der sechs Minispiele haben meine
Projektpartnerin und ich gemeinsam gebaut. Durch diese Schicht funktionieren Spielerauswahl,
Rundenwechsel und Ergebnisanzeige überall gleich. Von mir stammt das Event-System auf Basis von
Scriptable Objects. Ein Event ist ein Asset. Listener hängen sich im Inspector daran. Sender und
Empfänger müssen sich nicht kennen. Klare gemeinsame Schnittstellen waren auch der Grund, warum wir
parallel arbeiten konnten. Niemand musste dem anderen den Code umbauen.

## izzy.game1.1
Worum es geht

## izzy.game1.2
Minigolf Mayhem ist Minigolf aus der Third-Person-Perspektive. Es ist mit Abstand das größte und
aufwendigste meiner drei Spiele. Vier Spieler sind gleichzeitig auf demselben Kurs unterwegs. Der
eigentliche Gegner sind nicht die Fallen. Es sind die anderen Bälle. Wer trifft, schießt einen
fremden Ball weit weg. Diese Interaktion ist die Kernmechanik und kein Beiwerk.

## izzy.game1.3
Versteckt ist außerdem ein Easter Egg. Die Siegerehrung findet in der Disco aus Swaggy Snapshots
statt. Im Hintergrund wird getanzt.

## izzy.game1.4
Highlights & Herausforderungen

## izzy.game1.5
Physik mit Game Feel

## izzy.game1.6
Ein Schlag muss sich schwer und trotzdem kontrollierbar anfühlen. Ein weggeschossener Ball muss sich
lohnen. Er darf dem Getroffenen aber nicht die Runde ruinieren. Deshalb steckt die meiste Arbeit in
Game Feel und Physik.

## izzy.game1.7
Die Physik war der lange Teil. Ein dynamisches und chaotisches Spiel entsteht nicht dadurch, dass
Bälle hart aufeinander knallen. Es entsteht dadurch, dass das Ergebnis für beide Seiten noch
spielbar bleibt. Das habe ich über viele Durchläufe nachjustiert.

## izzy.game1.8
Computergegner mit GOAP

## izzy.game1.9
Die Computergegner laufen über einen selbst gebauten GOAP-Stack. Er besteht aus Planner, Agent,
Beliefs, Goals, Sensoren und Strategies und ist kein Asset. Damit plant ein NPC seinen Weg zum Loch.
Auf andere Bälle reagiert er dynamisch. Er versucht auch selbst, die Gegner am schnellen Abschluss
zu hindern. Stur den kürzesten Weg spielt er nicht.

## izzy.game1.10
GOAP war deutlich mehr Aufwand, als ich beim Start eingeplant hatte. Was ich daraus mitnehme: Der
Aufwand lohnt sich genau dort, wo die Gegner auf Unplanbares reagieren müssen. Eine feste Route
hätte funktioniert. Sie wäre aber sofort als Skript erkennbar gewesen. Damit wäre die Kernmechanik
ins Leere gelaufen.

## izzy.game2.1
Worum es geht

## izzy.game2.2
Auf der Tanzfläche einer Disco tanzen Tiere. Es gilt, im richtigen Moment ein Foto zu schießen.
Punkte gibt es für jede Eigenschaft, die ein Tier auf dem Bild erfüllt: lächeln, cool tanzen, in die
Kamera schauen. Mechanik und NPC-Logik sind entsprechend schlank. Der Reiz liegt im Timing und im
Bildausschnitt.

## izzy.game2.3
Highlights & Herausforderungen

## izzy.game2.4
Tanzanimationen von Hand

## izzy.game2.5
Das Highlight ist die Animationsarbeit. Sämtliche Tanzanimationen der Tiere habe ich Keyframe für
Keyframe von Hand gebaut. Dafür habe ich mich gründlich in das Animationssystem von Unity
eingearbeitet. Das war der Teil des Studiums, der am meisten Spaß gemacht hat. Er ist auch am
meisten hängen geblieben.

## izzy.game2.6
Am Ende fehlte die Zeit, die Animationen weiter zu glätten und mehr Tanzschritte zu ergänzen. Sie
erfüllen ihren Zweck. Ich sehe aber an jeder einzelnen, was noch gegangen wäre.

## izzy.game2.7
Einfache Mechanik schafft Freiraum

## izzy.game2.8
Aus diesem Spiel nehme ich zwei Dinge mit. Handwerklich ist es das Animationssystem. Konzeptionell
ist es die Erkenntnis, dass eine bewusst einfache Mechanik Freiraum schafft. Genau diesen Freiraum
haben die Animationen gebraucht.

## izzy.game3.1
Worum es geht

## izzy.game3.2
Bowling Battle ist Bowling mit Ballwahl. Jeder Ball rollt unterschiedlich gut. Dafür bringt er mehr
oder weniger Punkte pro umgeworfenem Pin. Vor dem Wurf verschiebt man den Ball nur seitlich und in
der Höhe. Danach fällt er und rollt über eine Rampe mit kleinen Hindernissen zu den Pins.

## izzy.game3.3
Highlights & Herausforderungen

## izzy.game3.4
Vier Bahnen ohne Trennwand

## izzy.game3.5
Alle vier Bahnen liegen direkt nebeneinander und haben keine Trennwand. Ein wild springender
Football kann also auf der Nachbarbahn landen. Dort punktet er dann für einen Gegner. So wird aus
einem Einzelspiel ein gemeinsames Chaos.

## izzy.game3.6
Am Ende jeder Bahn stehen kleine Hasenfiguren. Sie tauchen auch in den anderen Spielen der Sammlung
auf. Die Hasen schlagen die Bälle mit einem kräftigen Impuls zurück. So bekommt ein Ball eine zweite
Chance auf Pins. Oder er landet eben auf einer fremden Bahn.

## izzy.game3.7
Balance zwischen Zufall und Können

## izzy.game3.8
Die Schwierigkeit war die Balance. Ein schlecht rollender Ball muss sich über die höhere Punktzahl
wirklich lohnen. Sonst wählt ihn niemand. Gleichzeitig darf das Chaos zwischen den Bahnen gutes
Spielen nicht entwerten. Beides ist über Werte geregelt und hat mehrere Durchläufe gebraucht.

## izzy.game3.9
Was ich daraus mitnehme: Zufall macht ein Partyspiel nur dann besser, wenn er für alle am Tisch
sichtbar ist. Ein Ball, der sichtbar auf die Nachbarbahn springt, ist lustig. Ein unsichtbarer
Punktabzug wäre einfach nur unfair.

## izzy.main.9
Code ansehen

## izzy.detail-next.1
Nächstes Projekt: BullseyeQ

## izzy.detail-next.2
Kontakt
