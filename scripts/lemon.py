#!/usr/bin/env python3
"""Navigator for lemon-manuals.la — free car service manuals (LEMON + CHARM sets).

  lemon.py makes
  lemon.py years MAKE
  lemon.py cars MAKE YEAR [PATTERN]          # vehicles present for that year+db
  lemon.py index VEHICLE [--refresh]         # build/locate cached link index
  lemon.py find VEHICLE TERM... [--any] [-n N]
  lemon.py get PATH_OR_URL                   # clean text of one manual page
  lemon.py read VEHICLE TERM... [-n N]       # find + fetch best hit
  lemon.py torque VEHICLE [PART...] [-p N]   # torque pages, spec lines extracted
  lemon.py sub PATH_OR_URL                   # child pages under a hub page
  lemon.py imgs PATH_OR_URL                  # figure URLs on a page
  lemon.py pic URL                           # download a figure -> local path
  lemon.py note URL DESCRIPTION...           # save a vision description (persistent)
  lemon.py notes [URL]                       # show cached descriptions

VEHICLE is the site path without slashes, e.g. "Toyota/2015/Camry LE".
Stdlib only, Python 3.9+. Pages cache for 7 days (LEMON_TTL seconds, or
LEMON_NOCACHE=1); fetches retry and fail over to a mirror on their own.
"""
import hashlib, html as htmllib, json, os, re, ssl, sys, time
import urllib.error, urllib.parse, urllib.request

BASE = os.environ.get("LEMON_BASE", "https://lemon-manuals.la")
MIRRORS = ["https://lemon-manuals.la", "https://lemon-manuals.org.ua",
           "https://lemon-manuals.gy", "https://lemon.dogeware.me"]
CACHE = os.path.expanduser("~/.cache/lemon")
UA = "Mozilla/5.0 (X11; Linux x86_64) lemon-manuals-skill/2.1"
INDEX_VERSION = "2"                     # bump when the .idx layout changes
PAGE_TTL = int(os.environ.get("LEMON_TTL", 7 * 86400))
NOCACHE = os.environ.get("LEMON_NOCACHE") == "1"
RETRY = (408, 429, 500, 502, 503, 504)
NOT_FOUND = "<title>Page Not Found</title>"


def _ctx():
    caf = "/etc/ssl/certs/ca-certificates.crt"  # miniforge python ships no CA store
    return ssl.create_default_context(cafile=caf if os.path.exists(caf) else None)


def _bases():
    """LEMON_BASE first, then the mirrors that aren't it."""
    return [BASE] + [m for m in MIRRORS if m.rstrip("/") != BASE.rstrip("/")]


def _ours(url):
    return any(url.startswith(b) for b in _bases())


def _swap_base(url, base):
    for b in _bases():
        if url.startswith(b):
            return base + url[len(b):]
    return url


def _page_path(url):
    return os.path.join(CACHE, "pages", hashlib.md5(url.encode()).hexdigest() + ".html")


def _get(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx()) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return NOT_FOUND
        raise


def _try(url, timeout):
    """One host, retried on the errors that are worth retrying."""
    last = None
    for attempt in range(3):
        try:
            return _get(url, timeout)
        except urllib.error.HTTPError as e:
            if e.code not in RETRY:
                raise
            last = e
        except (urllib.error.URLError, OSError) as e:   # timeout, DNS, TLS
            last = e
        if attempt < 2:
            time.sleep(1 + 2 * attempt)
    raise last


def fetch(url, timeout=120, nocache=False):
    """Cached GET, retried, with mirror failover. never raises a bare traceback."""
    if url.startswith("/"):
        url = BASE + url
    if not url.endswith("/") and "?" not in url:
        url += "/"
    path = _page_path(url)
    if not (nocache or NOCACHE) and os.path.exists(path):
        if time.time() - os.path.getmtime(path) < PAGE_TTL:
            return open(path, encoding="utf-8").read()
    last = None
    for base in _bases():
        try:
            body = _try(_swap_base(url, base), timeout)
        except Exception as e:                          # this host is out, try the next
            last = e
            continue
        if not NOCACHE:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w", encoding="utf-8").write(body)
        return body
    sys.exit(f"all hosts failed for {url}: {last}")


def compact(u):
    """'Toyota/2015/Camry LE' -> '/Toyota/2015/Camry%20LE/'"""
    q = urllib.parse.quote(u.strip().strip("/"), safe="/,%&()'!$+-.:@")
    return "/" + q + "/"


def depth(url):
    return len([s for s in urllib.parse.urlparse(url).path.split("/") if s])


def makes():
    """Canonical make names, cached — the site is case-sensitive."""
    path = os.path.join(CACHE, "makes.txt")
    if os.path.exists(path):
        names = open(path, encoding="utf-8").read().split("\n")
    else:
        body = fetch(BASE + "/")
        names = [urllib.parse.unquote(u[len(BASE) + 1:].strip("/"))
                 for u, _ in links(BASE + "/", body) if depth(u) == 1]
        os.makedirs(CACHE, exist_ok=True)
        open(path, "w", encoding="utf-8").write("\n".join(names))
    return [n for n in names if n]


def canon_make(name):
    want = name.strip().lower().replace("-", " ").replace("_", " ")
    names = makes()
    for n in names:
        if n.lower().replace("-", " ") == want:
            return n
    for n in names:
        if want in n.lower().replace("-", " "):
            return n
    sys.exit(f"unknown make {name!r}. known: {', '.join(names)}")


def links(page_url, page_html):
    """(absolute_url, label) for every content link on a tree/index page."""
    out = []
    for m in re.finditer(r"<a\s+([^>]*)>(.*?)</a>", page_html, re.S | re.I):
        attrs, label = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        h = re.search(r"href=['\"]([^'\"]+)['\"]", attrs)
        if not h:
            continue
        href = htmllib.unescape(h.group(1))
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            continue
        u = urllib.parse.urljoin(page_url, href)
        if not _ours(u) or "/static/" in u or u.rstrip("/") == BASE:
            continue
        if any(x in u for x in ("/bundle/", "/hyperlink/", "style.css", "about.html")):
            continue
        out.append((u, re.sub(r"\s+", " ", htmllib.unescape(label)).strip()))
    return out


def text_of(page_html):
    h = re.sub(r"(?is)<title>.*?</title>", " ", page_html)
    h = re.sub(r'(?is)<div class="theme-colors header">.*?</div>', " ", h)
    h = re.sub(r'(?is)<div class="other-warning[^"]*">.*?</div>', " ", h)
    h = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", h)
    h = re.sub(r"(?is)<br\s*/?>", "\n", h)
    h = re.sub(r"(?is)</(p|div|li|tr|h[1-6]|table|ul|ol)>", "\n", h)
    h = re.sub(r"(?is)</t[dh]>", " | ", h)
    h = re.sub(r"(?s)<[^>]+>", "", h)
    h = htmllib.unescape(h)
    lines = []
    for raw in h.splitlines():
        line = re.sub(r"[ \t\xa0]+", " ", raw).strip()
        if not line or line.startswith("September 30: LEMON manuals"):
            continue
        if line.startswith("scientia non olet"):
            break
        lines.append(line)
    return "\n".join(lines)


def idx_path(vehicle):
    key = hashlib.md5((INDEX_VERSION + compact(vehicle)).encode()).hexdigest()[:16]
    return os.path.join(CACHE, key + ".idx")


def build_index(vehicle, refresh=False):
    path = idx_path(vehicle)
    if os.path.exists(path) and not refresh:
        return path
    v = compact(vehicle)
    pages = []
    for cand in (v + "Repair%20and%20Diagnosis%20%28Single%20Page%29/",
                 v + "Repair%20and%20Diagnosis/"):
        try:
            body = fetch(BASE + urllib.parse.quote(cand, safe="/%"), nocache=refresh)
        except Exception:
            continue
        if "Page Not Found" in body[:600]:
            continue
        pages.append((BASE + urllib.parse.quote(cand, safe="/%"), body))
        print(f"indexed {cand} ({len(body)//1024} KB)", file=sys.stderr)
        break
    if not pages:
        sys.exit(f"no Repair and Diagnosis tree for {vehicle!r} — check `cars` output")
    try:
        lt = BASE + v + "Labor%20Times/"
        body = fetch(lt, nocache=refresh)
        if "Page Not Found" not in body[:600] and "Labor times are only available" not in body:
            pages.append((lt, body))
            print("indexed Labor Times", file=sys.stderr)
    except Exception:
        pass
    seen, rows = set(), []
    for url, body in pages:
        for u, label in links(url, body):
            if u in seen or depth(u) < 4:
                continue
            seen.add(u)
            rows.append(f"{u}\t{label}")
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(rows))
    print(f"{len(rows)} pages indexed -> {path}", file=sys.stderr)
    return path


IMG_DIR = os.path.join(CACHE, "img")
NOTES = os.path.join(CACHE, "imgnotes.json")


def imgs_of(page_html):
    """Figure URLs on a page (site icons excluded)."""
    out = []
    for m in re.finditer(r"<img\s+([^>]*)>", page_html, re.I):
        a = m.group(1)
        src = re.search(r"src=['\"]([^'\"]+)['\"]", a)
        if not src or "/icons/" in src.group(1):
            continue
        u = urllib.parse.urljoin(BASE + "/", htmllib.unescape(src.group(1)))
        out.append(u if u.endswith("/") else u + "/")
    return out


def load_notes():
    return json.load(open(NOTES, encoding="utf-8")) if os.path.exists(NOTES) else {}


def sublinks(url, body):
    return [(u, l) for u, l in links(url, body) if u.startswith(url) and u != url]


def render(url, body=None):
    body = body if body is not None else fetch(url)
    if "Page Not Found" in body[:600]:
        sys.exit(f"404: {url}")
    out = [text_of(body)]
    notes = load_notes()
    for u in imgs_of(body):
        note = notes.get(u)
        out.append(f"[FIGURE {u}] {note}" if note else
                   f"[FIGURE {u}] (no cached description — vision it, then `note`)")
    subs = sublinks(url, body)
    if subs:
        out.append("[SUBPAGES]")
        out += [f"  {u}\t{l}" for u, l in subs]
    return "\n".join(out)


def read_page(url, terms, follow=4):
    """Render a page; if it is only a hub, follow the matching children."""
    body = fetch(url)
    print(render(url, body))
    subs = sublinks(url, body)
    if not subs:
        return
    want = [s for s in subs if any(t in norm(s[1] + " " + s[0]) for t in terms)] or subs
    for u, label in want[:follow]:
        print(f"\n{'=' * 70}\n## {label}\n")
        print(render(u))


def norm(s):
    """Search-friendly text: decoded, punctuation flattened, date tags dropped."""
    s = urllib.parse.unquote(s).lower()
    s = re.sub(r"[\[\]()&/\\|,]", " ", s)
    s = re.sub(r"\b\d{1,2}\s*\d{4}\b", " ", s)      # '09 2014' inside [09/2014 - ]
    s = re.sub(r"[-_+.]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def score(label, url, terms, need):
    hay = norm(label + " " + url)
    hit = [t for t in terms if t in hay]
    if len(hit) < need:
        return None
    lab = norm(label)
    s = 10 * len(hit) + 8 * sum(1 for t in terms if t in lab)
    return s - depth(url) / 4


def search(vehicle, terms, need=None, n=10):
    terms = [t.lower() for t in terms]
    need = need or max(1, len(terms) - 1)   # one spare term: users say 'pad', site says 'Brake'
    with open(build_index(vehicle), encoding="utf-8") as f:
        entries = [line.rstrip("\n").partition("\t")[::2] for line in f]
    # a URL that owns no children is a content page; a prefix of others is just a hub
    parents = {u.rstrip("/").rsplit("/", 1)[0] + "/" for u, _ in entries}
    rows = []
    for url, label in entries:
        s = score(label, url, terms, need)
        if s is not None:
            rows.append((s + (20 if url not in parents else 0), url, label))
    rows.sort(key=lambda r: (-r[0], len(r[1])))
    return rows[:n]


TORQUE_UNIT = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:N[.\s·*]*m\b|kgf[.\s·*]*cm\b|lb[.\s-]*(?:in|ft)\b|ft[.\s-]*lb\b)",
    re.I)


def torque_lines(page_text):
    """Lines that carry a torque figure, deduped, order kept. ponytail: prose lines, not a
    parsed table — the site prints one fastener per line, so a table is fiction until it isn't."""
    out, seen = [], set()
    for line in page_text.splitlines():
        line = line.strip(" |-")
        if not 6 <= len(line) <= 300 or not TORQUE_UNIT.search(line):
            continue
        key = re.sub(r"\W+", " ", line.lower()).strip()
        if key not in seen:
            seen.add(key)
            out.append(line)
    return out


def torque(vehicle, terms, want=3, cap=40):
    """Spec lines for a component. Component pages are often hubs, so descend one level."""
    rows = search(vehicle, list(terms) + ["torque"], need=1, n=80)

    def prefer(r):                       # part match first, spec pages next, "torque
        l = norm(r[2])                   # converter" is not a torque spec
        return (1 if "torque converter" in l else 0,
                sum(1 for t in terms if t.lower() not in l),
                0 if "specification" in l else 1)

    rows.sort(key=prefer)
    hits, seen = 0, set()
    for _, url, label in rows:
        if hits >= want:
            break
        if label in seen:
            continue
        seen.add(label)
        body = fetch(url)
        lines, target = torque_lines(text_of(body)), (url, label)
        for sub_url, sub_label in ([] if lines else sublinks(url, body)[:4]):
            if not lines:
                lines, target = (torque_lines(text_of(fetch(sub_url))),
                                 (sub_url, sub_label))
        if not lines:
            continue
        hits += 1
        print(f"\n## {target[1]}\n{target[0]}")     # raw URL: it is what `get` accepts
        print("\n".join(lines[:cap]))
    if not hits:
        sys.exit(f"no torque figures in {vehicle!r} for {' '.join(terms) or 'anything'}"
                 " — try `find VEHICLE torque specifications`")


def selftest():
    assert compact("Toyota/2015/Camry LE") == "/Toyota/2015/Camry%20LE/"
    assert norm("Brakes/Front%20Brake%20%5B09%2F2014%20-%20%5D") == "brakes front brake"
    h = ('<title>T</title><div class="theme-colors header">LEMON Manuals</div>'
         '<li><a href="X/">X</a></li><img alt="a" src="/images25/A/">'
         '<img src="/icons/wrench.svg">')
    assert imgs_of(h) == ["https://lemon-manuals.la/images25/A/"]
    assert "LEMON Manuals" not in text_of(h) and "X" in text_of(h)
    assert score("Torque Specifications", "/v/x/Torque/", ["torque"], 1) is not None
    assert score("Torque", "/v/x/Y/", ["brake"], 1) is None
    assert _swap_base("https://lemon-manuals.la/v/x/", "https://lemon.dogeware.me") \
        == "https://lemon.dogeware.me/v/x/"
    assert _page_path("/v/x/").endswith(".html")
    t = ("Tighten the bolts to 10 N.m (89 lb in).\n"
         "Oil pan bolts | 50 N·m (37 ft·lb)\n"
         "Fig 4: cylinder numbering 1 2 3\n")
    assert len(torque_lines(t)) == 2, torque_lines(t)
    assert torque_lines("no numbers here at all") == []
    b = "https://lemon-manuals.la/v/x/"
    assert [u for u, _ in sublinks(b, '<a href="y/">Y</a><a href="/v/x/">self</a>')] == [b + "y/"]
    print("selftest OK")


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[0], argv[1:]
    if cmd == "makes":
        print("\n".join(makes()))
    elif cmd == "years":
        make = urllib.parse.quote(canon_make(args[0]), safe="/%")
        for u, label in links(BASE + f"/{make}/", fetch(BASE + f"/{make}/")):
            if re.fullmatch(r"\d{4}", label):
                print(label)
    elif cmd == "cars":
        make, year = urllib.parse.quote(canon_make(args[0]), safe="/%"), args[1]
        pat = re.compile(args[2], re.I) if len(args) > 2 else None
        url = BASE + f"/{make}/{year}/"
        body = fetch(url)
        # emit vehicle links grouped by the database heading that precedes them
        pos_db = [(m.start(), m.group(1)) for m in re.finditer(r"Database:\s*([A-Za-z0-9_-]+)", body)]
        for m in re.finditer(r"<a\s+([^>]*)>(.*?)</a>", body, re.S | re.I):
            h = re.search(r"href=['\"]([^'\"]+)['\"]", m.group(1))
            if not h:
                continue
            label = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(2)))).strip()
            u = urllib.parse.urljoin(url, htmllib.unescape(h.group(1)))
            if depth(u) != 3 or not _ours(u):
                continue
            cur = [d for p, d in pos_db if p < m.start()]
            cur = cur[-1] if cur else "?"
            rel = urllib.parse.unquote(u[len(BASE) + 1:]).strip("/")
            if pat and not (pat.search(label) or pat.search(rel)):
                continue
            print(f"[{cur}] {rel}")
    elif cmd in ("index", "find", "read"):
        refresh, strict, anyw, n, pick = ("--refresh" in args, "--strict" in args,
                                          "--any" in args, 10, 1)
        for flag in ("-n", "-k"):
            if flag in args:
                i = args.index(flag)
                if flag == "-n":
                    n = int(args[i + 1])
                else:
                    pick = int(args[i + 1])
                args = args[:i] + args[i + 2:]
        args = [a for a in args if a not in ("--refresh", "--strict", "--any")]
        vehicle, terms = args[0], args[1:]
        if cmd == "index":
            build_index(vehicle, refresh)
            return
        if not terms:
            sys.exit("give search terms")
        need = len(terms) if strict else (1 if anyw else max(1, len(terms) - 1))
        rows = search(vehicle, terms, need, n)
        if not rows:
            sys.exit(f"no match in {vehicle!r} for {' '.join(terms)}")
        v = compact(vehicle)
        for s, url, label in rows:
            rel = urllib.parse.unquote(re.sub(r"^https?://[^/]+/", "", url).removeprefix(v.strip("/") + "/"))
            rel = re.sub(r"\s*\[\d{1,2}/\d{4} - \]", "", rel)
            print(f"{rel}\t{label}")
        if cmd == "read":
            print("\n" + "=" * 70 + "\n", file=sys.stderr)
            read_page(rows[min(pick, len(rows)) - 1][1], terms)
    elif cmd == "torque":
        if "-p" in args:
            i = args.index("-p")
            want, args = int(args[i + 1]), args[:i] + args[i + 2:]
        else:
            want = 3
        if not args:
            sys.exit("give a vehicle")
        torque(args[0], args[1:], want)
    elif cmd == "get":
        print(render(args[0]))
    elif cmd == "sub":
        body = fetch(args[0])
        for u, l in sublinks(args[0], body):
            print(f"{u}\t{l}")
    elif cmd == "imgs":
        print("\n".join(imgs_of(fetch(args[0]))))
    elif cmd == "pic":
        u = args[0]
        os.makedirs(IMG_DIR, exist_ok=True)
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120, context=_ctx()) as r:
            data = r.read()
            ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif"}.get(
                r.headers.get_content_type(), ".img")
        name = re.sub(r"\W+", "_", u.rstrip("/").split("/")[-1]) or "fig"
        out = os.path.join(IMG_DIR, name + ext)
        open(out, "wb").write(data)
        print(out)
    elif cmd == "note":
        u, desc = args[0], " ".join(args[1:])
        if not desc:
            sys.exit("give a description")
        os.makedirs(CACHE, exist_ok=True)
        notes = load_notes()
        notes[u] = desc
        json.dump(notes, open(NOTES, "w", encoding="utf-8"), indent=1, sort_keys=True)
        print(f"cached {u}")
    elif cmd == "notes":
        notes = load_notes()
        if args:
            print(notes.get(args[0], "(no cached description)"))
        else:
            for u, d in sorted(notes.items()):
                print(f"{u}\t{d[:120]}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except BrokenPipeError:      # piping into head/tail is normal use
        os._exit(0)
    except urllib.error.HTTPError as e:
        sys.exit(f"http {e.code} from {e.url} — the host may be down; try again or set LEMON_BASE")
    except KeyboardInterrupt:
        sys.exit(130)
