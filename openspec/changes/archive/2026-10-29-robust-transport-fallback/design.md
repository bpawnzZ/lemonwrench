# Design

## One choke point

Every request in the script already goes through `fetch()`, and every URL is
rewritten by `_swap_base()` against `_bases()`. So the whole change is the
transport block plus one helper (`imgs_of`); no command code is touched.

## Decisions

**charm.li in the mirror list, not a second code path.** Its paths are the same
shape as LEMON's CHARM pages (`/Make/Year/Vehicle/Repair and Diagnosis/…`), so
`_swap_base()` already produces working URLs for it. It is tried last: LEMON
holds newer books and LEMON's own CHARM pages, charm.li only the 2013-DVD era.
Over plain `http` — the `https` vhost 502s intermittently.

**Health file over in-process memory.** Each CLI invocation is a fresh process,
so the sticky/cooldown state has to be on disk to be worth anything:
`~/.cache/lemon/hosts.json` → `{"prefer": base, "down": {base: epoch}}`.
Failures cool for 15 min and are then retried; they sort last meanwhile rather
than being dropped, so a recovered host is picked back up without editing code.
`LEMON_BASE` still forces its host to the front and disables reordering — the
documented "pin one host" behaviour.

**404 and challenge pages are failures, not answers.** These are the two ways a
host replies 200-ish with garbage. The 404 came back as a *string* before, so
whichever host said "not found" first ended the search and its 29-byte body was
cached for 7 days. Both now raise inside `_get()`, are skipped per host, and are
never written to the page cache. Callers that already test for
`Page Not Found` in the body keep working: `fetch()` returns that sentinel only
when every host 404s.

**Wayback last.** If no host answers at all, ask
`archive.org/wayback/available` for a snapshot and fetch it with the `if_`
modifier (raw bytes, no archive banner). Costs one extra request only on total
failure, and it is the only path that can rescue a page when the project's
servers are gone for good — which is how the CHARM-era content will most likely
end up.

**Cooldown, not a circuit breaker.** ponytail: 15-minute cooldown, no adaptive
timeouts. Timeouts stay at 120 s and 3 attempts per host. Add per-host timeout
budgets if a *slow-but-alive* host starts dominating fetch time.
