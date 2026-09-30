## bullseyeq.main.1
← Back to the projects

## bullseyeq.main.2
BullseyeQ is a training app for darts players. It evaluates every throw and shows which drill will
help most next. It was built in Unity.

## bullseyeq.main.3.alt
Dashboard with the drill of the day, recent sessions and key metrics

## bullseyeq.main.4
The dashboard: drill of the day, recent sessions, key metrics.

## bullseyeq.main.5
The idea

## bullseyeq.main.6
Many darts players practise by feel. They throw at the treble 20 and hope to improve. Where the
points are really lost often stays unclear. This is exactly where BullseyeQ comes in. The app goes
along with practice right at the board and records every throw. After a few sessions it makes your
weaknesses visible.

## bullseyeq.main.7
The analysis leads to a concrete drill. You play it as a game mode of its own and not as a chore.
This is how BullseyeQ combines sports science with gameplay programming. Training theory says which
drill follows from which weakness. The game mechanics make sure you repeat it voluntarily.

## bullseyeq.main.8
What it is

## bullseyeq.main.9
BullseyeQ offers four training areas: scoring, 501, doubles and a training game against a computer
opponent. From the throws the app computes the usual darts metrics. These are the three-dart
average, the wasted-darts rate and the checkout rate. A heatmap shows where the darts actually land.
Line charts show the trend across all sessions.

## bullseyeq.main.10
From three completed sessions onwards a rule-based analysis kicks in. It names the most important
weak spot along with the matching training mode. Every recommendation shows the number it follows
from. In the training game you face an opponent that adapts to your level.

## bullseyeq.main.11
The trigger was my own darts practice. From the idea through the data model to the interface the app
was built together with a coding agent. The darts domain logic, the metrics and the thresholds come
from me. The UI graphics come from Layer Lab’s GUI-TheStone asset pack. Layout, theme and code are
mine.

## bullseyeq.main.12
Highlights & challenges

## bullseyeq.main.13.alt
Training plan with three prioritized recommendations, each with its current value, target and
matching training mode

## bullseyeq.main.14
The training plan: three recommendations by priority, each with the number it follows from.

## bullseyeq.main.15
Recommendations with reasons

## bullseyeq.main.16
A recommendation is only as good as its yardstick. Without a reference value a three-dart average is
just a number. So the real hurdle came before the code. I researched usable thresholds myself and
deliberately reduced them to a few tiers. Examples are an average below 35 or below 50 points.
Another is a wasted rate above 45 % against a target of 35 % at most.

## bullseyeq.main.17
That is no pro benchmark. The tiers give a rough classification and are not meant to do more. In
return the analysis does not guess. It calculates deterministically and traceably. The same throw
data always yields the same recommendation.

## bullseyeq.main.18.alt
Training game against the AI with the scoreboard, possible finishes and both sides’ throws

## bullseyeq.main.19
Training game against the DartAI: scoreboard, possible finishes and both sides’ throws.

## bullseyeq.main.20
An opponent on your level

## bullseyeq.main.21
Practice is more fun with an opponent who challenges you without overwhelming you. In the 501
training match the DartAI takes that role. It calibrates its T20 rate and its checkout rate to the
player’s last five legs. The T20 rate gets ±10 % variance. The checkout rate carries none. So the
opponent plays at roughly your own level and grows with you. Behind it is pure static logic with no
Unity dependency.

## bullseyeq.main.22.alt
Checkout Challenge with the route T9 D20, the list of attempts, hit rate and heatmap

## bullseyeq.main.23
The Checkout Challenge: route, attempts, hit rate and the session heatmap.

## bullseyeq.main.24
Drills as game modes

## bullseyeq.main.25
A recommendation does not become a note to self. It leads straight into a game mode that works on
the weakness it found. For finishing there is a checkout chart with the possible routes. On top come
dedicated checkout modes such as “Five Checkouts” and “Checkout Challenge”. An exercise that feels
like darts gets repeated. A spreadsheet does not.

## bullseyeq.main.26.alt
Scoring stats with line charts for average, triple and wasted rate, score distribution, dartboard
heatmap and session history

## bullseyeq.main.27
The scoring stats with the custom UI Toolkit elements: line charts and dartboard heatmap.

## bullseyeq.main.28
Tests and custom charts

## bullseyeq.main.29
You have to be able to rely on the analysis. That is why the app is covered by 565 EditMode test
cases in 20 test classes. They range from the domain logic to the contracts of the interface. The
domain logic includes the analyzer, the checkout chart and the 501 session. The JSON round trip of
the stored data is tested as well. For the stats views I built two custom UI Toolkit elements: a
dartboard heatmap and a line chart.

## bullseyeq.main.30
Working with a coding agent

## bullseyeq.main.31
BullseyeQ was also my test bed for working with a coding agent in Unity. I wanted to find out which
elements can be built that way and how. What I learned there shapes how I work today. I now know
better what I have to think through myself first. And I know what I can hand over.

## bullseyeq.main.32
View code

## bullseyeq.main.33
Try it in the browser

## bullseyeq.detail-next.1
Next project: Bob der Job-Bot

## bullseyeq.detail-next.2
Contact
