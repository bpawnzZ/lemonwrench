# Transport fallback: charm.li mirror, host health, Wayback last resort

## Why

`fetch()` walks a fixed mirror list and treats the *first* host that answers
anything as the answer. That fails three ways, all seen on 2026-10-29 while
looking up G6 torque specs:

1. **`lemon-manuals.la` went to nginx 504s and ~3 KB/s.** A 5.5 MB single-page
   index was 25+ minutes away; `index` was abandoned twice. The CHARM-era
   corpus is also published at `charm.li`, which served the same 2.9 MB tree in
   6 seconds — but the script has no idea that host exists.
2. **A 404 poisoned the page cache.** `_get()` returns the `Page Not Found`
   body instead of raising, so the first host to 404 "wins" and the garbage is
   written to `~/.cache/lemon/pages/` for 7 days. Same class of bug for
   Cloudflare challenge pages (`lemon.dogeware.me` returns 200 + a JS
   challenge).
3. **Every request re-hammers the dead host.** There is no memory of which host
   answered last, so each `fetch` pays the full timeout on the broken host
   again.

## What Changes

- Add `http://charm.li` (Operation CHARM, the upstream of LEMON's CHARM set) to
  the failover list.
- Cache host health in `~/.cache/lemon/hosts.json`: the last host that worked is
  tried first; a host that errored is tried **last** for 15 minutes (never
  dropped).
- A 404 from one host no longer ends the search and never gets cached; only an
  all-host 404 returns the `Page Not Found` sentinel the callers already
  expect.
- Cloudflare challenge bodies are treated as a host failure, not a page.
- Last resort: if every host fails, try the Wayback Machine snapshot of the URL
  before giving up.
- `imgs_of()` resolves root-relative figure paths against the page they came
  from, so figures keep working when the page came from a non-default host.

## Impact

- `scripts/lemon.py` only (transport + `imgs_of`); CLI surface unchanged, no new
  dependency (stdlib only), Python 3.9+ preserved.
- Offline `selftest` gains assertions for host ranking, 404/challenge rejection
  and base swapping, so CI covers the new logic without a network.
