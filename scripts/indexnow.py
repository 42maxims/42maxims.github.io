#!/usr/bin/env python3
"""Submit 42maxims.com URLs to IndexNow (Bing, Yandex, Seznam, Naver and others share submissions).

Run after a deploy has finished (the key file must be live):
    python3 scripts/indexnow.py                 # every URL in sitemap.xml
    python3 scripts/indexnow.py --since HEAD~1  # only pages whose HTML changed since that git revision
    python3 scripts/indexnow.py --dry-run       # print the payload, send nothing
Exit 0 on HTTP 200/202 (or nothing to submit), 1 otherwise.
"""
import argparse, json, os, re, subprocess, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10000


def build_constants():
    src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
    key = re.search(r'^INDEXNOW_KEY = "([0-9a-f]{32})"', src, re.M).group(1)
    site = re.search(r'^SITE_URL = "([^"]+)"', src, re.M).group(1)
    return key, site


def sitemap_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as fh:
        return re.findall(r"<loc>([^<]+)</loc>", fh.read())


def changed_urls(since, site, known):
    """Sitemap URLs whose generated index.html changed between `since` and HEAD."""
    out = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", since, "HEAD", "--", "*.html"],
                         check=True, capture_output=True, text=True).stdout.split()
    urls = []
    for f in out:
        if f == "index.html" or f.endswith("/index.html"):
            u = f"{site}/{f[:-len('index.html')]}"
            if u in known:
                urls.append(u)
    return urls


def payload(key, site, urls):
    host = site.split("//", 1)[1]
    return {"host": host, "key": key, "keyLocation": f"{site}/{key}.txt", "urlList": urls[:MAX_URLS]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", help="git revision: submit only pages changed since it")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    key, site = build_constants()
    known = sitemap_urls()
    urls = changed_urls(a.since, site, set(known)) if a.since else known
    if not urls:
        print("indexnow: nothing to submit")
        return 0
    body = payload(key, site, urls)
    if a.dry_run:
        print(json.dumps(body, indent=1))
        return 0
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "42maxims-indexnow"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        print(e.read().decode(errors="replace")[:500], file=sys.stderr)
    print(f"indexnow: submitted {len(body['urlList'])} URLs, HTTP {status}")
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
