---
name: lemonwrench
description: "Use when looking up car repair procedures, torque specs, diagrams or service-manual steps. Scrapes free OEM manuals by vehicle, resolves the exact trim/engine, and cross-checks parts catalogs and field sources."
version: 2.1.0
author: LemonWrench contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cars, repair, service-manual, torque-specs, diagrams, lemon-manuals]
    related_skills: [web-search, ocr-and-documents]
---

# LemonWrench — automotive repair research

Turns "how do I replace X on <car>" into a **procedure, a torque table, and labelled
figures** — then cross-checks it against a parts catalog and real-world field notes
so you don't chase a step the manual left out.

Primary source: **https://lemon-manuals.la** — ~10,000 US/Canada vehicles across **69 makes, 1960–2025**, free, no login. Domestic, import, orphan brands (Pontiac, Oldsmobile, Saturn, Saab, AMC, Geo, Mercury, Suzuki), Euro exotics, trucks/commercial, and modern EVs (Tesla 2012→, Rivian 2022→). Years run deep, not just recent: Toyota and Ford carry 66 straight model years. Real HTML text (torque tables, capacities, step-by-step), figures at `/images25/`. Not scanned PDFs.

Two databases per model year:

| DB | Source | Use it for |
|---|---|---|
| **LEMON** | 2025 capture | 2010+, current TSBs, complete trees, figure captions |
| **CHARM** | 2013 DVDs | 1990s–2000s, finer detail, trees truncated at depth |

## The three-source rule

A manual alone is not an answer. Every confident answer here comes from three:

1. **The manual** — the procedure and the torque figures.
2. **A parts catalog** (gmpartscenter.net, gmpartsdirect.com, rockauto, etc.) — part
   numbers, and *structural proof*: if two castings are separate parts, they're
   separate parts. This is how you answer "is this bracket part of the cover?"
   without guessing from a photo.
3. **Field consensus** (model forums, JustAnswer/identifix threads, YouTube
   transcripts) — the steps the manual omits because the engineer never turned the
   wrench. Say plainly when a step is field consensus rather than manual text.

If the three disagree, report the disagreement. Never paper over it.

## The tool

```
S=scripts/lemon.py          # relative to the skill dir; use an absolute path if you prefer
python3 $S <cmd>
```

Every command below takes that same `$S`.

| Command | Purpose |
|---|---|
| `makes` | canonical make names |
| `years MAKE` | model years present |
| `cars MAKE YEAR [regex]` | vehicles for that year, tagged `[LEMON]` / `[CHARM]` |
| `index VEHICLE [--refresh]` | fetch + cache the whole link tree (once per vehicle) |
| `find VEHICLE TERM... [-n N] [--strict\|--any]` | grep the cached tree |
| `read VEHICLE TERM... [-k N]` | render the Nth hit, auto-following hub sub-pages |
| `torque VEHICLE [PART...] [-p N]` | torque pages + every spec line extracted |
| `get URL` | render one page by absolute URL |
| `sub URL` | child pages under a hub |
| `imgs URL` / `pic URL` / `note URL TEXT` / `notes [URL]` | figure pipeline + persistent cache |
| `selftest` | parser checks, no network |

`VEHICLE` is the site path minus slashes: `Toyota/2015/Camry LE`,
`Pontiac/2007/G6 V6-3.9L`.

## Workflow

1. **Resolve the car properly.** `cars MAKE YEAR` lists every variant. Engine and
   trim change the manual — `G6 GT, 4D Sedan, 3.9 1, Automatic` is a different book
   from `G6 GT, 4D Sedan, 3.5 N`. Say which variant you used. Note that a badge can
   lie: the same nameplate shipped with several engines, so confirm displacement.
2. **Index once.** LEMON single-page tree ≈ 5.5 MB / 13k links, CHARM split tree
   ≈ 1.3 MB. Cached at `~/.cache/lemon/<hash>.idx`; later queries are local greps.
   `--refresh` only when the site adds manuals.
3. **Search in site vocabulary** — `removal`, `installation`, `disassembly`,
   `torque specifications`, `fluid capacities`, `valve clearance`,
   `component locations`, `wiring diagram`, `DTC`, `labor times`. Default allows one
   unmatched term; `--strict` for exact, `--any` for one-word fishing.
4. **Read, and escalate.** `read` prints hits then the best page's text then follows
   sub-pages. CHARM trees are depth-truncated: a hub page often lists nothing until
   you `sub <url>` and then `get <url>`. Two-level escalation is normal, not a bug.
5. **Answer**: numbered steps, torques exactly as printed, page URL, and a
   confidence note per claim (`manual` / `catalog` / `field`).

## Figures

`read`/`get` emit `[FIGURE https://lemon-manuals.la/images25/XXXX/]` lines, with a
cached description appended when one exists.

```
python3 $S pic https://lemon-manuals.la/images25/GM1557668/   # -> ~/.cache/lemon/img/GM1557668.png
# view it, then:
python3 $S note https://lemon-manuals.la/images25/GM1557668/ "right rocker cover, bolt ring, coil bracket above"
```

Captions in the page text (`Fig 1: View Of Right Valve Rocker Arm Cover`) are the
figure's real title — use them, they're accurate even when the scan is illegible.
Transcribe what a scan *says* (callout numbers, part labels); never infer what it
*means*. A numbered callout you can read is evidence; "this looks like one casting,
not two" from a 1-bit line-art scan is not, and the same figure will read both ways on
two passes. Structural and fastener questions are settled by the parts catalog and the
step list, not by the picture. Scans with no labels (plain routing views) give you the
shape of the job and nothing else — say that rather than narrating detail that isn't
there. Worth pulling: exploded views (they carry torque callouts the text omits),
wiring diagrams, connector end views.

Descriptions persist in `~/.cache/lemon/imgnotes.json` — describe a diagram once and
it's text forever.

## Beyond the manual

- **Structural questions** ("is this part of the timing cover?") → parts catalog.
  Separate part number + separate gasket = separate casting. The catalog diagram
  also tells you which sub-assembly a fastener belongs to.
  Start with **gmpartscenter.net** — it serves a plain `Diagram N: <name>` list with
  P/N, `Positions:` (Left/Right/front) and `Notes: PARTS: Part included with …`,
  which is exactly the evidence needed: the front cover is one P/N *with its gasket
  included*, so anything carrying a different P/N is a different casting. Some
  catalogs answer `http_error`/403 to a plain fetch; that is a property of the site,
  not a dead end — move to another catalog instead of concluding the part is
  undocumented.
- **Access questions** ("what's blocking this bolt?") → field sources. Search
  `<year> <model> <engine> "<part>" bracket bolt` and read the forum/JustAnswer
  threads; dealer techs post the missing steps.
- **Whether a tool is needed** (`pressed-on pulley`, `Torx`, `stud`) → the removal
  procedure's preliminary steps; they name the special tools (e.g. `J 25034-C`).
- **Aftermarket electronics on the car** (remote start, key-out/idle run, bypass
  modules, alarm integration) → not a service-manual question. The service info
  gives you the wiring (ignition switch connector, Passlock type, BCM location);
  the answer about what a module *does* lives in the module maker's vehicle
  install guide. Search `<year> <model> "<module brand>" install guide` and work from
  the maker's vehicle-specific PDF, not the generic manual.
- **Bolt torque for a part you can't identify** → torque table by component name,
  then confirm the casting by part number. Same-looking brackets on one engine
  often carry different specs (e.g. 25 N·m vs 50 N·m on adjacent parts).

## User photos of the car

A phone photo is evidence of a *question*, not an answer. When the user sends engine-bay
pictures to settle "is this part of the timing cover?":

- **Never settle the structure from the image.** Vision descriptions of grimy cast aluminium
  come back fluent and self-contradicting — the same photo reads as one continuous casting in
  one pass and two separate parts in the next, with invented head types and bolt counts.
  Treat any description as a hypothesis; never quote its bolt count back as fact.
- **Settle it with the catalog**: separate part number + separate gasket = separate casting.
  Quote both P/Ns so the user can check the casting in their hand.
- **Give a physical test they can run in a minute** — does the joint weep oil when its
  fasteners are cracked loose (a sealed cover does, a bolted bracket doesn't); does the part
  carry accessory holes (bracket) or a gasket rail (cover); does the cover behind it keep its
  own continuous bolt ring.
- Ask for a **wide shot** when geometry is still unclear. Close-ups of dirty aluminium are
  genuinely ambiguous — saying so is better than a confident wrong answer.
- **Moulded digits need a crop, not a whole-frame glance.** A 4032×3024 phone photo of a
  grimy casting downsamples to mush, and vision will confidently invent a sequence — it
  read `6,1 / 5,2 / 4,3` off a pack whose actual labels were `1,2,3 / 4,5,6`. Cut the frame
  down first:
  `magick photo.jpg -auto-orient -resize 200% -sharpen 0x1 -contrast-stretch 2%x2% big.jpg`,
  then crop the component and vision each crop separately; tesseract is useless under moiré.
  **Cross-check the read against physics** — towers sharing a coil must be three firings
  apart in the firing order (1&4, 2&5, 3&6 on a 1-2-3-4-5-6 V6), so a reading that pairs
  1&6 or 2&3 is wrong no matter how clear the pixels looked. A self-consistent transcription
  from two independent crops is evidence; one pass is a hypothesis.

## Orientation: engine frame vs car frame

Any answer that says "front", "rear", "left" or "right" about an engine is ambiguous until the
frame is named. On a transverse install the two frames are 90° apart and getting this wrong makes a
correct torque list useless.

- **Engine front = the belt/accessory end. Car front = the radiator.** Say which one you mean every
time (`the belt end (engine front, passenger side of the car)`). Nine tenths of orientation errors are
this collision, and the manual's own figures use the *engine* frame — an arrow labelled FRONT in a
cylinder-ID drawing points at the belt, not the bumper.
- **Cylinder numbering starts at the engine front** and walks toward the transaxle end. So the two
cylinders nearest the belt are #1 and #2; the two nearest the transaxle are the highest pair.
- **Anchor the banks to hardware, not to geometry prose or a catalog label.** Deriving left/right by
  imagining where you stand relative to the crank flips every other time. Use something the user can
  see: the bank the coil pack bolts to, the bank whose cover procedure lists the generator, the bank
  with the oil filler. State the anchor as the rule ("the bank with the coil pack is 1-3-5") so the
  user can verify it in seconds. A parts catalog's `Positions: Left / Right / Passenger Side` is the
  manufacturer's own frame, not the car's view of it — on a transverse install those disagree, and
  taking the label literally is how a diagram ends up mirrored against the user's own photo.
- **Draw in the user's stated frame, not plan view.** If they say "I'm standing at the front bumper,
my left is the passenger side", then left of the drawing is the belt end, the near edge is the
radiator bank and the far edge is the firewall bank. Label all four edges before placing any numbers.
Put one recognisable part per bank in the drawing (oil cap, coil pack) so the user can map it onto the
car in their head.
- When a photo is supplied, quote what it actually fixes: "belt left, coil on the far bank, oil cap
near" — then draw to that. Do not re-derive the orientation from first principles afterwards.
- **Keep one diagram, current.** Rewrite the canonical file rather than adding `-v2` next to a wrong
  one; two layouts that disagree are worse than none. If a file write is refused because the file was
  not read in full this task, read it **whole** — a `limit=`/offset read still fails the guard — then
  replace it; or write the fixed version to a new path and delete the stale one in the same breath.

## Answering rules

- Quote torques exactly, all three units: `34 N*m (350 kgf*cm, 25 ft*lbf)`.
- Call out low-torque fasteners explicitly (valve covers, plastic/composite covers):
  over-torquing into aluminium is the top cause of repeat leaks and pulled threads.
- `[09/2014 - ]` in a path is a revision date — that page applies from then on.
- LEMON pages often say the manual "is identical to the following model variants,
  except possibly Labor Times, Fluids, and Tire Fitment" — reuse instead of re-searching.
- `<vehicle>/Labor Times/` lists Remove & Replace operations; if it says "only
  available for a different vehicle variant", use the variant it names.
- Not covered? Say so plainly and name the nearest covered year. Never invent a spec.
- **A page can exist while the table you need does not.** Tower maps, connector
  pinouts, wire-by-wire routing and cylinder→terminal charts frequently have no page
  at all, even where firing order and cylinder ID do. Check the obvious homes (coil
  replacement, ignition-cable/plug-wire procedure, description & operation, specs,
  diagrams index) — then **read the part itself before saying the map isn't published**.
  Castings and moulded plastic carry what the manual omits: cylinder numbers beside coil
  towers, pin numbers in connector shells, alignment dots, the pairing of a waste-spark
  column. "Not in the service info" is not "not documented", and sending the user to ring
  a wire out with a meter when the number is moulded on the tower wastes their daylight.
  Do not synthesise a map from a figure either.
- When the map is missing, give the **physical method** instead of a guess: moulded
  wire assemblies index one way through their clips (one side at a time; long wires
  cross to the far bank); identify the bank from the cylinder-ID figure, not memory;
  and the durable fix is a marker pen or an ohmmeter before removal. Flag
  family conventions (e.g. waste-spark pairs) as unverified unless the manual states
  them.
- Sequencing matters: read the **preliminary procedures** of the part the user actually
  wants off, then recurse into each of those — that chain is the real disassembly order
  and it routinely reaches three or four parts deep (cover → crossover pipe → PS pump →
  idler pulleys → belt). Never give the last step alone.

## Deliverable

Write the result as a standalone markdown note, not chat prose:

- frontmatter (`tags`, `vehicle`, `job`, `status`, `updated`)
- status callout — where the job actually stands
- the direct answer to the blocking question, first
- numbered procedure per side/component
- one torque table covering every fastener touched
- captioned figure embeds
- **sources/confidence table** — claim, source, verified / field consensus

See `examples/` for a complete worked note, and `references/repair-writeup.md` for the
full write-up procedure: how to reconcile manual against field reality, the note's
section order, the confidence column, and how to hand the figures over.

## Gotchas

- URLs are case-sensitive and the make spelling is the site's (`Dodge and Ram`,
  `Mercedes Benz`); `canon_make` handles it, manual curl does not.
- Trailing slashes matter on every directory URL.
- `/bundle/` zip downloads are **disabled** (303 → `/static/sad.html`). `robots.txt`
  disallows `/bundle/` too.
- `/hyperlink/...` URLs are the cross-reference resolver, not content.
- Paths contain version tags and `%2F`-encoded slashes: fetch only the absolute URL
  the tool printed; re-quoting a decoded path 404s.
- Banner "back up on a temporary server / slowness possible" is skipped by the
  parser; allow 120 s timeouts.
- Mirrors: `lemon-manuals.org.ua`, `lemon-manuals.gy`, `lemon.dogeware.me`. The
  script fails over to them automatically on a timeout or 429/5xx; `LEMON_BASE=https://…`
  pins one host and disables failover.
- Pages are cached under `~/.cache/lemon/pages/` for 7 days (`LEMON_TTL` seconds
  overrides; `index --refresh` bypasses). `LEMON_NOCACHE=1` disables the cache entirely.
- Python 3.9+ (`str.removeprefix`). Stdlib only.
- Miniforge/pyenv pythons often ship no CA bundle; `lemon.py` falls back to
  `/etc/ssl/certs/ca-certificates.crt`.

## Verify

```
python3 $S selftest                                    # expects: selftest OK
python3 $S torque "Toyota/2015/Camry LE" brake         # expects: spec lines, no traceback
```
