## bob.main.1
← Back to the projects

## bob.main.2
Bob is a job scanner for several users. Every find lands in a shared pool. Scoring happens
separately for each profile. The service runs live with real fellow users.

## bob.main.3
The idea

## bob.main.4
Anyone looking for a job searches the same portals as everyone else. Each person searches alone and
starts anew every day. Most listings get discarded again. The question behind Bob was: why is
everyone actually searching alone?

## bob.main.5
Bob turns that around. Every find lands in a shared pool. Scoring still happens per profile. Not
every interesting job is the right one for you. For someone else it may be the dream job. So a
listing I discard is not lost. It shows up for the member whose profile it fits.

## bob.main.6
What it is

## bob.main.7
Bob collects job listings from several job portals into a shared pool. It scores each listing
against the criteria of the profile in question. A web app with an in-app inbox shows the result.
Underneath sits a FastAPI application with SQLite for storage. An MCP server in the same app makes
the same data directly accessible from Claude Code. Access is limited per user.

## bob.main.8
Bob runs as a closed alpha with fellow students. Feedback arrives through a feedback widget straight
from the app. Transparency mattered to me. The source code is public. The member kit for scanning
uses nothing but each member’s own Claude subscription. So no API costs arise.

## bob.main.9
The project covers scraping, data model, scoring, web interface, MCP server and running it on my own
server. Bob was my first large project outside the engine. It was also the first I developed end to
end with my own harness and self-built skills. The AI writes along. The architecture, the security
questions and operations are mine.

## bob.main.10
Scoring starts with fixed rules and only turns to an LLM when in doubt. Scanning is not done by the
server. The members do it over their own connection. A security audit and more than 1,200 tests
safeguard the service.

## bob.main.11
Highlights & challenges

## bob.main.12
Rules decide first

## bob.main.13
Scoring starts deterministically. A rule engine with 25 weighted criteria and 25 hard no-go vetoes
scores every listing without an LLM. The LLM only runs on the “maybe” band. That is where the rules
alone cannot decide. Thumbs-up and thumbs-down votes adjust the weights.

## bob.main.14
Only the job pool is shared and that is deliberate. Criteria, ratings and insights stay strictly per
profile. The same listing can be scored completely differently for two members. The ratings never
mix.

## bob.main.15
The hurdle was the IP and not the browser

## bob.main.16
Collecting is the least reliable part of the system. Portals change their markup, throttle requests
and detect automated access. For a long time it looked like a problem of browser disguise. Then a
live test disproved that assumption and revealed the actual cause.

## bob.main.17
The decisive step in scraping was not a trick but a diagnosis. The portals block data-centre IPs. So
the problem was not the browser fingerprint. It was the reputation of the server’s IP. From the data
centre it did not work. From a residential connection it did.

## bob.main.18
That became the architecture. Scanning is not done automatically by the server. The members scan
themselves by command in their own Claude Code and over their own connection from home. The finds
land in the shared pool via the MCP server. The server adds aggregators such as Adzuna and Jooble
using each member’s own keys. That experience changed how I work. Today I first check a theory with
the smallest real test I can run. Only then do I build on it.

## bob.main.19
Security around other people’s access

## bob.main.20
This brings foreign content and other people’s access into play. So a lot of the work is in security
and reliability. That includes a token per member, data access limited per user and protection
against prompt injection at the MCP boundary. CSRF and SSRF safeguards and a hardened SQLite layer
come on top. A security audit produced five findings. Among them was a cross-tenant hole rated HIGH.
All five are fixed. Each fix has its own test.

## bob.main.21
Running it for others

## bob.main.22
The second hard part was that Bob does not run just for me. As soon as others join in, they
experience every source of error themselves. Three examples: a login works only for me. Mail
delivery fails silently without the right domain records. A test suite is green while the site still
serves old files live. This is where systematically recording decisions and lessons learned first
proved itself over weeks in production. That way the same mistake does not happen twice.

## bob.main.23
Above all the project shows that I work my way into an unfamiliar stack on my own. I do not just get
it running. I keep it running. Bugs that surface after weeks in production are a different category
from bugs in a hand-in. Operations here means a daily SQLite backup, a health check with alerting
and SemVer patch releases. On top come more than 1,200 tests. They make sure a fix breaks nothing
else.

## bob.main.24
Still open: the hit rate

## bob.main.25
The hit rate is still open. It differs from portal to portal. A browser scan today returns far more
listings than usable matches. Detecting expired listings is just as tedious as collecting them. Both
are documented on the list.

## bob.main.26
Roadmap

## bob.main.27
Next up is application writing. Cover letters and CVs are then generated from the job and company
data of a listing. After that come application tracking, a mobile app and gamification elements.

## bob.main.28
View code

## bob.detail-next.1
Next project: Desk-Buddy

## bob.detail-next.2
Contact
