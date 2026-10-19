---
name: lemonwrench
description: "Use when looking up car repair procedures, torque specs, diagrams or service-manual steps. Scrapes free OEM manuals by vehicle, resolves the exact trim/engine, and cross-checks parts catalogs and field sources."
version: 2.0.0
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
S=scripts/lemon.py
python3 $S <cmd>
```

| Command | Purpose |
|---|---|
| `makes` | canonical make names |
| `years MAKE` | model years present |
| `cars MAKE YEAR [regex]` | vehicles for that year, tagged `[LEMON]` / `[CHARM]` |
| `index VEHICLE [--refresh]` | fetch + cache the whole link tree (once per vehicle) |
| `find VEHICLE TERM... [-n N] [--strict\|--any]` | grep the cached tree |
| `read VEHICLE TERM... [-k N]` | render the Nth hit, auto-following hub sub-pages |
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
1-bit line art reads fine at full size. Worth looking at: exploded views (they carry
torque callouts the text omits), wiring diagrams, connector end views.

Descriptions persist in `~/.cache/lemon/imgnotes.json` — describe a diagram once and
it's text forever.

## Beyond the manual

- **Structural questions** ("is this part of the timing cover?") → parts catalog.
  Separate part number + separate gasket = separate casting. The catalog diagram
  also tells you which sub-assembly a fastener belongs to.
- **Access questions** ("what's blocking this bolt?") → field sources. Search
  `<year> <model> <engine> "<part>" bracket bolt` and read the forum/JustAnswer
  threads; dealer techs post the missing steps.
- **Whether a tool is needed** (`pressed-on pulley`, `Torx`, `stud`) → the removal
  procedure's preliminary steps; they name the special tools (e.g. `J 25034-C`).
- **Bolt torque for a part you can't identify** → torque table by component name,
  then confirm the casting by part number. Same-looking brackets on one engine
  often carry different specs (e.g. 25 N·m vs 50 N·m on adjacent parts).

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
- Sequencing matters: give the prerequisite chain (belt → accessory → bracket →
  cover), not just the cover bolts.

## Deliverable

Write the result as a standalone markdown note, not chat prose:

- frontmatter (`tags`, `vehicle`, `job`, `status`, `updated`)
- status callout — where the job actually stands
- the direct answer to the blocking question, first
- numbered procedure per side/component
- one torque table covering every fastener touched
- captioned figure embeds
- **sources/confidence table** — claim, source, verified / field consensus

See `examples/` for a complete worked note.

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
- Mirrors if the main host dies: `lemon-manuals.org.ua`, `lemon-manuals.gy`,
  `lemon.dogeware.me` — `LEMON_BASE=https://…` overrides.
- Miniforge/pyenv pythons often ship no CA bundle; `lemon.py` falls back to
  `/etc/ssl/certs/ca-certificates.crt`.

## Verify

```
python3 scripts/lemon.py selftest      # expects: selftest OK
```
