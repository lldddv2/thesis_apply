#!/usr/bin/env python3
"""
Download a paper PDF given a DOI or URL.
Tries: direct URL → Unpaywall (open access) → Sci-Hub.
Usage: python download_paper.py <DOI or URL> [-o output.pdf]
"""

import sys
import re
import argparse
import urllib.request
import urllib.parse
import urllib.error
import json
from pathlib import Path

SCIHUB_MIRRORS = [
    "https://sci-hub.box",
    "https://sci-hub.se",
    "https://sci-hub.st",
    "https://sci-hub.ru",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def is_doi(s: str) -> bool:
    return bool(re.match(r"^10\.\d{4,}/\S+$", s.strip()))


def normalize_input(s: str) -> tuple[str | None, str | None]:
    """Return (doi, url). One may be None."""
    s = s.strip()
    # Extract DOI from a URL like https://doi.org/10.xxxx/...
    doi_from_url = re.search(r"10\.\d{4,}/\S+", s)
    if doi_from_url:
        doi = doi_from_url.group(0).rstrip(")")  # clean trailing parens
        url = s if s.startswith("http") else None
        return doi, url
    if s.startswith("http"):
        return None, s
    return None, None


def fetch_url(url: str, output_path: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
            if b"%PDF" in data[:8] or "pdf" in content_type:
                output_path.write_bytes(data)
                return True
    except Exception:
        pass
    return False


def try_unpaywall(doi: str, output_path: Path) -> bool:
    """Query Unpaywall for an open-access PDF URL."""
    email = "thesis@example.com"
    api = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}"
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        best = data.get("best_oa_location") or {}
        pdf_url = best.get("url_for_pdf") or best.get("url")
        if pdf_url:
            print(f"  Unpaywall found: {pdf_url}")
            return fetch_url(pdf_url, output_path)
    except Exception:
        pass
    return False


def try_scihub(doi: str, output_path: Path) -> bool:
    for mirror in SCIHUB_MIRRORS:
        url = f"{mirror}/{doi}"
        print(f"  Trying Sci-Hub mirror: {url}")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")

            # 1. citation_pdf_url meta tag (sci-hub.box style)
            pdf_match = re.search(
                r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']',
                html,
            )
            # 2. iframe/embed src ending in .pdf
            if not pdf_match:
                pdf_match = re.search(
                    r'(?:src|href)=["\']([^"\']*\.pdf[^"\']*)["\']', html
                )
            # 3. JS location.href redirect
            if not pdf_match:
                pdf_match = re.search(
                    r'location\.href=["\']([^"\']+)["\']', html
                )
            if pdf_match:
                pdf_url = pdf_match.group(1)
                if pdf_url.startswith("//"):
                    pdf_url = "https:" + pdf_url
                elif pdf_url.startswith("/"):
                    pdf_url = mirror + pdf_url
                print(f"  PDF link: {pdf_url}")
                if fetch_url(pdf_url, output_path):
                    return True
        except Exception:
            continue
    return False


def default_filename(doi_or_url: str) -> str:
    safe = re.sub(r"[^\w\-.]", "_", doi_or_url.replace("/", "_"))
    return safe[:80] + ".pdf"


def main():
    parser = argparse.ArgumentParser(description="Download a paper PDF from DOI or URL.")
    parser.add_argument("input", help="DOI (e.g. 10.1103/PhysRevD.11.2042) or full URL")
    parser.add_argument("-o", "--output", help="Output PDF filename", default=None)
    args = parser.parse_args()

    doi, url = normalize_input(args.input)

    if doi is None and url is None:
        # Maybe it's a bare DOI without http prefix
        if is_doi(args.input):
            doi = args.input.strip()
        else:
            print("Error: could not parse input as a DOI or URL.")
            sys.exit(1)

    out_name = args.output or default_filename(doi or url)
    output_path = Path(out_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Target: doi={doi}  url={url}")
    print(f"Output: {output_path}")

    # 1. Direct URL download
    if url:
        print("\n[1/3] Trying direct URL...")
        if fetch_url(url, output_path):
            print(f"Downloaded to {output_path}")
            return

    # 2. Unpaywall
    if doi:
        print("\n[2/3] Trying Unpaywall (open access)...")
        if try_unpaywall(doi, output_path):
            print(f"Downloaded to {output_path}")
            return

    # 3. Sci-Hub
    if doi:
        print("\n[3/3] Trying Sci-Hub...")
        if try_scihub(doi, output_path):
            print(f"Downloaded to {output_path}")
            return

    print("\nFailed to download PDF from all sources.")
    sys.exit(1)


if __name__ == "__main__":
    main()
