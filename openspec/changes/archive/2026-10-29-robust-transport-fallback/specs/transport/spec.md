# Transport capability

## ADDED Requirements

### Requirement: Host failover with health memory

The fetcher SHALL try every configured manual host before failing, SHALL prefer
the host that last answered, and SHALL order a recently failed host last for a
cool-down period without removing it from the list.

#### Scenario: primary host is down

- **GIVEN** the preferred host returns 504 or times out
- **WHEN** any command fetches a page
- **THEN** the fetcher tries the remaining hosts and returns the first real page
- **AND** the dead host is recorded so the next call does not start with it

#### Scenario: pinned host

- **GIVEN** `LEMON_BASE` is set in the environment
- **WHEN** a page is fetched
- **THEN** that host is tried first

### Requirement: Replies that are not pages are skipped

The fetcher SHALL treat a 404 body and a Cloudflare challenge body as a failure
of that host for that URL, SHALL NOT write either to the page cache, and SHALL
return the not-found sentinel only when every host reports not-found.

#### Scenario: one host lacks the page

- **GIVEN** host A answers 404 and host B has the page
- **WHEN** the page is fetched
- **THEN** host B's content is returned and cached

#### Scenario: every host lacks the page

- **GIVEN** all hosts answer 404
- **WHEN** the page is fetched
- **THEN** the callers receive the not-found sentinel and nothing is cached

### Requirement: Archive fallback

The fetcher SHALL attempt an Internet Archive snapshot of the URL when every
configured host fails.

#### Scenario: all hosts unreachable

- **GIVEN** every host errors
- **WHEN** an archived snapshot exists
- **THEN** the snapshot content is returned

### Requirement: Figures resolve against their own page

Figure URLs SHALL be resolved relative to the page they were found on, so a page
served by a fallback host yields that host's figure URLs.

#### Scenario: page from a fallback host

- **GIVEN** a page served by host B containing `<img src="/images/X/1/">`
- **WHEN** its figures are listed
- **THEN** the URL starts with host B
