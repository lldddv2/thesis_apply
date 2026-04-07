#!/usr/bin/env python3
"""
Search papers on OpenAlex by keyword/title/author.
Returns a list of results with DOI, title, authors, year, open-access URL.

Usage:
    python openalex_search.py "kerr geodesics analytical" [-n 10]
    python openalex_search.py "Boyer-Lindquist" --year-from 2000 --year-to 2024
"""

import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
from dataclasses import dataclass

BASE_URL = "https://api.openalex.org/works"
EMAIL = "thesis@example.com"  # polite pool — faster responses

HEADERS = {
    "User-Agent": f"thesis-paper-downloader/1.0 (mailto:{EMAIL})"
}


@dataclass
class PaperResult:
    title: str
    doi: str | None
    year: int | None
    authors: list[str]
    open_access_url: str | None
    openalex_id: str

    def short_doi(self) -> str | None:
        if self.doi:
            return re.sub(r"https?://doi\.org/", "", self.doi)
        return None

    def display(self, index: int) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        doi_str = self.short_doi() or "no DOI"
        oa_str = f"  OA: {self.open_access_url}" if self.open_access_url else "  OA: no"
        return (
            f"[{index}] {self.title}\n"
            f"     {authors_str} ({self.year})\n"
            f"     DOI: {doi_str}\n"
            f"{oa_str}"
        )


def search_openalex(
    query: str,
    n: int = 10,
    year_from: int | None = None,
    year_to: int | None = None,
) -> list[PaperResult]:
    params = {
        "search": query,
        "per-page": str(n),
        "select": "id,title,doi,publication_year,authorships,open_access,best_oa_location",
        "mailto": EMAIL,
    }

    filters = []
    if year_from:
        filters.append(f"publication_year:>{year_from - 1}")
    if year_to:
        filters.append(f"publication_year:<{year_to + 1}")
    if filters:
        params["filter"] = ",".join(filters)

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    results = []
    for item in data.get("results", []):
        authors = [
            a["author"]["display_name"]
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]

        oa = item.get("open_access", {})
        oa_url = oa.get("oa_url")
        if not oa_url:
            best = item.get("best_oa_location") or {}
            oa_url = best.get("pdf_url") or best.get("landing_page_url")

        results.append(PaperResult(
            title=item.get("title") or "(sin título)",
            doi=item.get("doi"),
            year=item.get("publication_year"),
            authors=authors,
            open_access_url=oa_url,
            openalex_id=item.get("id", ""),
        ))

    return results


def main():
    parser = argparse.ArgumentParser(description="Search papers on OpenAlex.")
    parser.add_argument("query", help="Search query (title, keywords, author)")
    parser.add_argument("-n", "--results", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--year-from", type=int, default=None, help="Filter: published from year")
    parser.add_argument("--year-to", type=int, default=None, help="Filter: published up to year")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    try:
        results = search_openalex(
            query=args.query,
            n=args.results,
            year_from=args.year_from,
            year_to=args.year_to,
        )
    except Exception as e:
        print(f"Error querying OpenAlex: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No results found.")
        return

    if args.json:
        out = [
            {
                "title": r.title,
                "doi": r.short_doi(),
                "year": r.year,
                "authors": r.authors,
                "open_access_url": r.open_access_url,
            }
            for r in results
        ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"\n{len(results)} resultados para: '{args.query}'\n")
    for i, r in enumerate(results, 1):
        print(r.display(i))
        print()


if __name__ == "__main__":
    main()
