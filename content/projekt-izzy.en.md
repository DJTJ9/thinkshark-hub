## izzy.main.1
← Back to the projects

## izzy.main.2
Izzy’s Island Party is a collection of six mini-games for one to four players. It is my final
project in the Games Programming course at SAE Institute Hamburg. We built it as a team of two in
Unity 6 from November 2025 to March 2026.

## izzy.main.3
The idea

## izzy.main.4
The basic idea was a collection of funny mini-games that you could also play at a party. That is why
you play locally against each other. Computer opponents fill any empty seats. You play with a
controller or the keyboard.

## izzy.main.5
The mini-games were split cleanly. Three were mine and three were my project partner’s. Mine are
Minigolf Mayhem, Swaggy Snapshots and Bowling Battle. I built them on my own, from the game
mechanics to the computer opponents. We kept design and ideas aligned throughout.

## izzy.main.6
This project was built without coding agents and without any other AI help. I wrote the code for my
three games myself. That makes it the clearest evidence of what I can carry to a playable state on
my own inside a running team project. Along the way I stick to shared interfaces and do not bend
them to suit me.

## izzy.main.7
The shared foundation

## izzy.main.8
My project partner and I built the game framework, menu, player management and the integration of
the six mini-games together. This layer makes player selection, turn rotation and the score screen
work the same everywhere. The event system based on Scriptable Objects is mine. An event is an
asset. Listeners hook into it in the Inspector. Sender and receiver never need to know each other.
Clear shared interfaces are also why we could work in parallel. Neither of us had to rewrite the
other’s code.

## izzy.game1.1
What it is

## izzy.game1.2
Minigolf Mayhem is third-person minigolf. It is by far the largest and most involved of my three
games. Four players move across the same course at the same time. The real opponent is not the
hazards. It is the other balls. Hit one and you send it flying. That interaction is the core
mechanic and not a garnish.

## izzy.game1.3
There is also an easter egg tucked away. The award ceremony takes place in the disco from Swaggy
Snapshots. There is dancing in the background.

## izzy.game1.4
Highlights & challenges

## izzy.game1.5
Physics with game feel

## izzy.game1.6
A shot has to feel weighty and still controllable. Knocking someone’s ball away has to pay off. It
must not ruin the round for the player who got hit. That is why most of the work went into game feel
and physics.

## izzy.game1.7
The physics were the long haul. A dynamic and chaotic game does not come from balls slamming into
each other. It comes from the outcome staying playable for both sides. That took many passes to
tune.

## izzy.game1.8
Computer opponents with GOAP

## izzy.game1.9
The computer opponents run on a GOAP stack I built myself. It consists of planner, agent, beliefs,
goals, sensors and strategies and is not an asset. With it an NPC plans its way to the hole. It
reacts dynamically to other balls. It also actively tries to keep its rivals from finishing quickly.
It does not stubbornly play the shortest line.

## izzy.game1.10
GOAP turned out to be considerably more work than I had budgeted for at the start. What I take from
it: the effort pays off exactly where opponents have to react to something you cannot plan in
advance. A fixed route would have worked. It would have read as a script straight away. The core
mechanic would have fallen flat.

## izzy.game2.1
What it is

## izzy.game2.2
Animals dance on a disco floor. The goal is to take the photo at the right moment. You score a point
for every trait an animal fulfils in the shot: smiling, dancing well, looking into the camera.
Mechanics and NPC logic are lean accordingly. The appeal is in the timing and the framing.

## izzy.game2.3
Highlights & challenges

## izzy.game2.4
Dance animations by hand

## izzy.game2.5
The highlight is the animation work. I hand-built every dance animation for the animals keyframe by
keyframe. To do that I worked my way properly into Unity’s animation system. It was the part of my
degree that was the most fun. It is also the part that stuck with me the most.

## izzy.game2.6
In the end I ran out of time to smooth the animations further and add more moves. They do their job.
But I can see on every single one what else would have been possible.

## izzy.game2.7
A simple mechanic makes room

## izzy.game2.8
I take two things from this game. On the craft side it is the animation system. On the design side
it is the insight that a deliberately simple mechanic frees up room. The animations needed exactly
that room.

## izzy.game3.1
What it is

## izzy.game3.2
Bowling Battle is bowling with a choice of ball. Each ball rolls better or worse. In return it pays
out more or fewer points per pin it knocks down. Before the throw you only shift the ball sideways
and in height. Then it drops and rolls down a ramp with small obstacles towards the pins.

## izzy.game3.3
Highlights & challenges

## izzy.game3.4
Four lanes with no divider

## izzy.game3.5
All four lanes sit directly next to each other with no divider. So a wildly bouncing football can
end up on the neighbouring lane. There it scores for an opponent. That turns a single-player game
into shared chaos.

## izzy.game3.6
At the end of every lane stand little bunny figures. They also show up in the other games of the
collection. The bunnies whack the balls back with a hefty impulse. That gives a ball a second shot
at the pins. Or it lands on someone else’s lane.

## izzy.game3.7
Balancing chance and skill

## izzy.game3.8
The difficulty was balance. A badly rolling ball has to genuinely pay off through the higher score.
Otherwise nobody picks it. At the same time the chaos between lanes must not make good play
irrelevant. Both are governed by tuning values and took several passes.

## izzy.game3.9
What I take from it: randomness only improves a party game when everyone at the table can see it. A
ball visibly bouncing onto the next lane is funny. An invisible point deduction would just be
unfair.

## izzy.main.9
View code

## izzy.detail-next.1
Next project: BullseyeQ

## izzy.detail-next.2
Contact
