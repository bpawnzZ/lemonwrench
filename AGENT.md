# AGENT.md — lemonwrench

Handoff note for any agent picking this repo up. Read this before editing.

## What this is

A skill + one stdlib Python tool (`scripts/lemon.py`, ~640 lines) that reads free
OEM service manuals (LEMON 2025 capture + CHARM 2013 DVDs) and answers car-repair
questions: torque specs, procedures, figures, labor times.

- `SKILL.md` — the procedure an agent follows (three-source rule, figure pipeline,
  answering rules). **This is the product.** `scripts/lemon.py` serves it.
- `README.md` — user-facing.
- `examples/` — two worked notes + committed figure scans.
- `openspec/` — spec-driven changes; `openspec/changes/archive/` is the history.
- `.github/workflows/ci.yml` — offline `selftest` on Python 3.9 / 3.12 / 3.13.

Installed copy (what Hermes actually loads):
`~/.hermes/skills/research/lemon-manuals/{SKILL.md,scripts/lemon.py}`.
**After every change here, copy both files there** or the running skill keeps the
old code.

## Current state (v2.2.0)

Transport hardened: mirror chain with host health, plus an archive last resort.

| Piece | Value |
|---|---|
| Chain | `lemon-manuals.la` → `charm.li` → `org.ua` → `gy` → `dogeware` |
| Sticky host | `~/.cache/lemon/hosts.json` (`prefer` + `down{}`) |
| Cooldown | `DOWN_FOR` 900 s — failed host sorts last, never dropped |
| Per-host silence | `PER_HOST` 45 s (a streaming host is never cut off) |
| Chain cap | `LEMON_BUDGET`, default 240 s |
| Last resort | `archive.org/wayback/available` + `if_` raw fetch |
| Not-a-page | 404 body and `cdn-cgi/challenge-platform` raise `NotFound` / `Blocked`, never cached |

## Traps

- **The site is often the problem, not the code.** On 2026-10-29
  `lemon-manuals.la` returned nginx 504s at ~3 KB/s; a 5.5 MB `index` was 25+
  minutes away and two runs had to be killed. `charm.li` served the same tree in
  ~6 s. If `index` crawls, `get` the charm.li tree page and grep it locally.
- **`charm.li` is `http`, not `https`** (the TLS vhost 502s intermittently), has
  the whole tree expanded on one page, links are **single-quoted**, and it has no
  `Repair and Diagnosis (Single Page)` path and no 2010+ manuals.
- **Never trust a 200.** Cloudflare challenge pages come back as 200 with a JS
  wall (`lemon.dogeware.me` does this) — that's why `_challenge()` exists.
  Before v2.2 a 404 "won" the fetch and its 29-byte body was cached for 7 days.
- **`archive.org` 429s from some networks** (observed here). `_wayback()` treats
  that as "no archive" and returns `None`; that path is code-complete but has not
  been seen to return a snapshot from this host.
- Figures are 1-bit scans with no printed callouts. Don't invent bolt counts or
  captions from them; the parts catalog settles structure.
- Cache: `~/.cache/lemon/{pages,*.idx,img,imgnotes.json,hosts.json}`. Delete
  `hosts.json` to reset host preference.

## Verify (copy-paste)

```bash
cd ~/git/lemonwrench
python3 scripts/lemon.py selftest              # offline, must print "selftest OK"
python3 scripts/lemon.py --help | head -3

# failover still works: pin a dead host, expect a real page back (~45-90 s)
rm -f ~/.cache/lemon/hosts.json
LEMON_BASE=https://lemon-manuals.invalid LEMON_NOCACHE=1 python3 scripts/lemon.py get \
  "/Pontiac/2007/G6%20V6-3.5L/Repair%20and%20Diagnosis/Starting%20and%20Charging/Charging%20System/Alternator/Service%20and%20Repair/Generator%20Bracket%20Replacement%20%28LZ4%29/" \
  | grep "Tighten the bolts in sequence"     # expect: ... to 50 N.m (37 lb ft)

# second call should be ~1 s off the remembered host
cat ~/.cache/lemon/hosts.json                # expect prefer == the host that answered

# sync the installed skill
cp SKILL.md scripts/lemon.py ~/.hermes/skills/research/lemon-manuals/ 2>/dev/null || {
  cp SKILL.md ~/.hermes/skills/research/lemon-manuals/SKILL.md
  cp scripts/lemon.py ~/.hermes/skills/research/lemon-manuals/scripts/lemon.py; }
```

## Change flow

`openspec-propose` → implement → `openspec validate <change> --strict` →
verify with the commands above → `git commit` → `openspec archive <change>`.
Don't add dependencies: stdlib only, Python 3.9+, one file.
