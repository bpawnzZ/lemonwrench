# Tasks

## 1. Transport

- [x] 1.1 Add `http://charm.li` to the mirror list.
- [x] 1.2 Host health file (`hosts.json`): preferred host first, cooling hosts
      last; 15-minute cooldown after a failure.
- [x] 1.3 Raise on 404 and on Cloudflare challenge bodies inside `_get()`; treat
      both as "this host is no use for this page".
- [x] 1.4 `fetch()`: only return the `Page Not Found` sentinel when **every**
      host 404s; never cache a 404 or a challenge page.
- [x] 1.5 Wayback snapshot as the last resort when all hosts fail.
- [x] 1.6 `imgs_of()` resolves against the page URL.

## 2. Verification

- [x] 2.1 Extend `selftest` for ranking, 404/challenge rejection, charm.li swap.
- [x] 2.2 `python3 scripts/lemon.py selftest` passes.
- [x] 2.3 Live: with a dead `LEMON_BASE` pinned, a page still comes back via the
      fallback chain (proves the failover, not just the parser).
- [x] 2.4 Live: a real CHARM page renders through charm.li.
- [x] 2.5 CI matrix (3.9 / 3.12 / 3.13) still green.

## 3. Docs

- [x] 3.1 SKILL.md gotchas + README mention the charm.li mirror, host health and
      Wayback.
- [x] 3.2 AGENT.md written for the repo.
