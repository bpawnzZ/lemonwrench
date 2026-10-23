# Delivering a repair write-up

How to turn manual pages into the artifact the user actually wants: a durable note on disk, not a
chat answer that evaporates.

## 1. Reconcile manual vs. field reality

Manuals describe the engine on a stand as often as in the car, and occasionally skip a step the
job forces. When the user is mid-job and blocked by a specific piece of hardware:

1. Give the manual's step list verbatim first — it establishes the real fastener/torque set.
2. Then search the exact symptom in the user's words plus the displacement and the part:
   `"<year> <model> <displacement>" "<blocking part>" <job>`. Search two engines (Google and a
   smaller index) — the forum/JustAnswer hits that answer "the manual doesn't mention this
   bracket" only exist there.
3. Prefer hits that quote manufacturer/dealer procedure or name a torque — a forum reply saying
   "you have to pull the bracket" plus an expert answer quoting the neighbouring-engine
   procedure is enough to state the rule, and you say which of the two you're relying on.
4. Mark it: manual-sourced = ✅ verified, field consensus = ⚠️ field consensus. Never upgrade a
   forum answer to verified because it agreed with your guess.

## 2. Answer the blocker in the first two sentences

The user is standing at the car. Lead with the direct yes/no on their actual question ("it is
not part of the timing cover"), then the *proof* from the manual's own step list, then the
how-to. A ranked how-to that names the wrong part first wastes their daylight.

Name the alternatives when the hardware is ambiguous — "if it's the cast bracket the alternator
sat in, do this; if it's the coil bracket, 25 N·m" — rather than picking one and being wrong.

## 3. The note

Put it where the user keeps notes (vault, repo, wiki) and match the existing notes' style rather
than inventing a new one. Filename `YYYY-MM-DD-<make>-<model>-<engine>-<job>.md` sorts and greps
well:

- frontmatter: `tags:` (automotive, repair, guide, make, model), `updated:`, `vehicle:`, `job:`,
  `status:` when the job is in progress
- a `> [!info]` status callout stating where the job stands, and a `> [!tip]` one-line answer
- numbered contents block, then one `##` section per stage
- **torque table with every fastener on the job in one place**, all three units as printed
- `> [!warning]` callouts for the mistake that ruins the job (over-torqued bolts into
  aluminium, wrong tightening sequence, prying a machined face)
- a closing **Sources / confidence** table: claim → source → ✅ verified / ⚠️ field consensus,
  plus an explicit "not verified" list. State the limits of what was checked — most readers
  check that column first.

## 4. Figures

Download each figure with `pic`, copy the PNGs next to the note (e.g. `attachments/<slug>/`), and
embed them the way that note format embeds images — wikilinks in Obsidian, relative markdown
elsewhere — with the manual's `Fig N:` caption as the italic line beneath. The user reads the
line art; the note just has to carry it. Never leave remote `lemon-manuals.la` image URLs as the
only copy: the note has to survive the site.

## 5. Close the loop

Give the note's absolute path in the reply plus the short in-chat version: the direct answer, the
removal order, and the torque table. The chat answer is the summary; the note is the deliverable.

When the write-up is headed for a messaging platform, send the **torque table as the message
body and the note as a file attachment** — a full procedure with tables blows past message
limits and mangles on paste, while the file survives intact and is forwardable to the garage.

If the chat client renders images, print the figures into the reply as well (one image per line
with a one-line caption above it). A note full of wikilinks hands the user nothing to look at
while they are standing at the car.

Then **close the loop into memory** if the harness has durable memory: retain the facts worth
reusing — the torque set for this engine, part numbers that settled a structural question, a
layout correction that supersedes something previously stored. Write the correction explicitly
("supersedes the earlier note that put 1-3-5 on the radiator bank") rather than adding a second,
contradicting fact and leaving recall to pick.
