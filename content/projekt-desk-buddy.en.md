## desk-buddy.main.1
← Back to the projects

## desk-buddy.main.2
in progress

## desk-buddy.main.3
Desk-Buddy is a desktop pet for Windows. The longer you sit, the more the character slouches. A
short exercise straightens it up again. It is currently a prototype.

## desk-buddy.main.4
The idea

## desk-buddy.main.5
The idea comes straight from sports science. Movement breaks work once they become a habit. Habits
form through motivation and feedback and not through nagging.

## desk-buddy.main.6
So Desk-Buddy does not remind you like a timer. It sits at the desk with you and notices when you
have been sitting too long. The model is the Tamagotchi mechanic and not the timer popup. That is
why it did not become a notification. It became a character whose posture you look after.

## desk-buddy.main.7
What it is

## desk-buddy.main.8
Desk-Buddy is a transparent desktop pet in Unity. It runs on top of the Windows desktop. The
character’s posture decays in stages with your own sitting time. There is no popup and no sound. The
character does not take focus away either. When to respond is up to you.

## desk-buddy.main.9
The core loop runs as a Windows build. A click on the character opens a choice of time window. The
options are 30 seconds, 2, 5 or 15 minutes. That produces an exercise plan from a database of 28
exercises. The character demonstrates each one with intro, loop and outro. Its posture recovers
along the way.

## desk-buddy.main.10
Desk-Buddy is in progress and deliberately has no repo link. It is currently a prototype. The code
depends on things I am not allowed to publish. Final IK is a purchased asset. The SMPL-X body model
in the mocap chain is under a non-commercial research licence. I developed Desk-Buddy together with
AI. The idea, the structure and the motion-capture pipeline are my decisions.

## desk-buddy.main.11
The overlay is a layer of its own at the window level of Windows. The load model runs through a
simulated working day in milliseconds. For the exercise clips a local motion-capture chain has
emerged. It works with self-shot videos.

## desk-buddy.main.12
Highlights & challenges

## desk-buddy.main.13
An overlay without help from the engine

## desk-buddy.main.14
Unity is not meant for desktop overlays. A frameless window with a transparent background that stays
permanently on top is not an engine feature. It is work at the operating system’s window level.

## desk-buddy.main.15
So the overlay is a Win32 interop layer of its own. The 3D character is rendered straight into the
back buffer of a borderless and transparent window. A topmost re-assert keeps the window in front.
On top of that comes a click-through state machine with a drag lock. I built it test-first. That
first hurdle is behind me.

## desk-buddy.main.16
A working day in milliseconds

## desk-buddy.main.17
The load model behind the character is free of Unity and gets its clock injected. That lets a
simulated working day run through in EditMode in milliseconds and not in real time. EditMode tests
cover the logic. The state is persisted and survives a restart.

## desk-buddy.main.18
A local motion-capture chain

## desk-buddy.main.19
The bigger piece is the motion-capture chain that came out of it. It runs entirely locally:
self-shot video → GVHMR under WSL2 → headless Blender → FBX → Unity. Cleanup runs through Final IK.
In an A/B comparison on the same clip the local chain beat the paid service. By now the pipeline is
a project of its own and split out as a package.

## desk-buddy.main.20
The second hurdle was the pipeline itself. Capture, cleanup and baking had to get far enough that a
clean loop comes out at the end. Grounding and jitter damping are part of that. Otherwise the
character floats or trembles. It is not finished. Standing exercises are still untested.

## desk-buddy.main.21
What is still open

## desk-buddy.main.22
What is still open is above all producing the 28 exercise clips. So far everything runs on
placeholder clips. More posture idles will follow. Six are planned. Everyday practicalities such as
autostart and multi-monitor support are still missing too. That is exactly why I call it a prototype
and not a finished product.

## desk-buddy.detail-next.1
Next project: Izzy's Island Party

## desk-buddy.detail-next.2
Contact
