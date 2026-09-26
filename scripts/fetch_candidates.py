"""Fetch recent, verified candidate papers for the Paper of the week routine.

Runs in GitHub Actions (full internet). Queries OpenAlex for papers published in the
last 60 days (90 as a fallback) on the project's topics, drops anything already in
papers.json, pulls authoritative metadata from Crossref, and writes candidates.json.
The cloud routine (which has no web access) reads candidates.json and writes the notes.

Standard library only.
"""
import json, re, sys, time, datetime, html, urllib.request, urllib.parse

MAILTO = "valentynakundas@gmail.com"
UA = f"paper-of-the-week/1.0 (mailto:{MAILTO})"
WINDOW_DAYS = 60
FALLBACK_DAYS = 90
MAX_CANDIDATES = 25

QUERIES = [
    "alfalfa rhizosphere microbiome drought",
    "Medicago sativa rhizosphere bacteria water stress",
    "Medicago rhizosphere microbiome",
    "rhizosphere microbiome drought root exudate",
    "root exudation drought bacteria",
    "microbiome selection passaging generations plant",
    "host-mediated microbiome selection",
    "experimental evolution rhizosphere microbiome transfer",
    "combined stress drought light plant microbiome",
    "stress combination plant rhizosphere",
    "shade light intensity rhizosphere bacteria",
    "photoperiod root microbiome",
    "Sinorhizobium meliloti drought nodulation",
    "rhizobia nodulation water deficit legume",
    "legume grass intercropping rhizosphere bacteria",
    "plant competition rhizosphere microbiome assembly",
    "sterilized soil microbiome inoculation plant growth",
    "soil microbiome transplant plant performance",
    "compositional data analysis microbiome amplicon",
    "longitudinal microbiome statistics mixed model",
    "pot experiment replication experimental unit plant microbiome",
    "soil water potential microbial drought pot experiment",
]

# words that raise the relevance of a candidate for her project
BOOST = {
    "alfalfa": 4, "medicago": 4, "rhizosphere": 2, "drought": 2, "water deficit": 2, "exudat": 2,
    "selection": 2, "passag": 3, "generation": 1, "light": 1, "shade": 2, "photoperiod": 2,
    "combined": 2, "sinorhizobium": 3, "rhizobi": 2, "nodul": 2, "legume": 1, "grass": 1,
    "steril": 2, "transplant": 1, "inocul": 1, "compositional": 2, "16s": 1, "amplicon": 1,
    "bacteria": 1, "microbiome": 1,
}
PENALTY = {"review": 3, "meta-analysis": 1, "perspective": 2, "human": 3, "gut": 4, "mouse": 3, "clinical": 4, "cancer": 5, "fish": 2, "shrimp": 3}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa
            if i == tries - 1:
                print("WARN", url[:120], e, file=sys.stderr)
                return None
            time.sleep(2 + 2 * i)


def abstract_from_inverted(inv):
    if not inv:
        return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[i] for i in sorted(pos))


def clean(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip())


def openalex(query, from_date):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "filter": f"title_and_abstract.search:{query},from_publication_date:{from_date},type:article",
        "sort": "relevance_score:desc",
        "per-page": 12,
        "select": "title,doi,publication_date,primary_location,authorships,abstract_inverted_index,relevance_score",
        "mailto": MAILTO,
    })
    d = get(url)
    return (d or {}).get("results", [])


def crossref(doi):
    d = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    if not d:
        return None
    m = d["message"]
    parts = None
    for k in ("published-online", "published", "issued", "created"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            parts = dp[0]
            break
    date = None
    if parts:
        y, mo, da = (list(parts) + [1, 1])[:3]
        date = f"{y:04d}-{mo:02d}-{da:02d}"
    return {
        "title": clean((m.get("title") or [""])[0]),
        "journal": clean((m.get("container-title") or [""])[0]),
        "authors": [(a.get("given", "") + " " + a.get("family", "")).strip() for a in m.get("author", [])],
        "published": date,
        "type": m.get("type"),
        "abstract": clean(m.get("abstract", "")),
    }


def score(c):
    text = (c["title"] + " " + c["abstract"]).lower()
    s = c.get("relevance", 0) / 100.0
    for w, v in BOOST.items():
        if w in text:
            s += v
    for w, v in PENALTY.items():
        if w in text:
            s -= v
    if len(c["abstract"]) < 300:
        s -= 3
    s += min(len(c["hits"]), 4) * 1.5
    return round(s, 2)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    today = datetime.date.today()
    papers = json.load(open("papers.json", encoding="utf-8"))
    used = {w["doi"].lower() for w in papers.get("weeks", []) if w.get("doi")}
    used |= {c["doi"].lower() for c in papers.get("classics", []) if c.get("doi")}

    found = {}
    for days in (WINDOW_DAYS, FALLBACK_DAYS):
        from_date = (today - datetime.timedelta(days=days)).isoformat()
        for q in QUERIES:
            for w in openalex(q, from_date):
                doi = (w.get("doi") or "").replace("https://doi.org/", "").lower()
                if not doi or doi in used:
                    continue
                c = found.get(doi)
                if c is None:
                    src = (w.get("primary_location") or {}).get("source") or {}
                    c = {
                        "doi": doi,
                        "title": clean(w.get("title")),
                        "journal": src.get("display_name"),
                        "publication_date": w.get("publication_date"),
                        "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
                        "abstract": clean(abstract_from_inverted(w.get("abstract_inverted_index"))),
                        "relevance": w.get("relevance_score") or 0,
                        "hits": [],
                        "window_days": days,
                    }
                    found[doi] = c
                if q not in c["hits"]:
                    c["hits"].append(q)
            time.sleep(0.3)
        if len(found) >= 8:
            break

    cands = list(found.values())
    for c in cands:
        c["score"] = score(c)
    cands.sort(key=lambda c: c["score"], reverse=True)
    cands = cands[:MAX_CANDIDATES]

    # authoritative metadata + date check from Crossref
    verified = []
    for c in cands:
        cr = crossref(c["doi"])
        time.sleep(0.5)
        if not cr or not cr["title"]:
            continue
        pub = cr["published"] or c["publication_date"]
        try:
            age = (today - datetime.date.fromisoformat(pub)).days
        except Exception:
            continue
        if age > FALLBACK_DAYS or age < -3:
            continue
        c.update({
            "title": cr["title"] or c["title"],
            "journal": cr["journal"] or c["journal"],
            "authors": cr["authors"] or c["authors"],
            "published": pub,
            "age_days": age,
            "crossref_type": cr["type"],
        })
        if len(cr["abstract"]) > len(c["abstract"]):
            c["abstract"] = cr["abstract"]
        c["doi_url"] = "https://doi.org/" + c["doi"]
        c.pop("publication_date", None)
        verified.append(c)

    out = {
        "generated_at": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "window_days": WINDOW_DAYS,
        "fallback_days": FALLBACK_DAYS,
        "note": "Candidates published recently, not already in papers.json, metadata from Crossref, abstracts from OpenAlex/Crossref. Ranked by a keyword score; the routine makes the final choice and writes the notes.",
        "candidates": verified,
    }
    json.dump(out, open("candidates.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(verified)} verified candidates written (from {len(found)} found)")
    for c in verified[:10]:
        print(f"  {c['score']:>5} | {c['published']} | {c['journal']} | {c['title'][:90]}")


if __name__ == "__main__":
    main()
