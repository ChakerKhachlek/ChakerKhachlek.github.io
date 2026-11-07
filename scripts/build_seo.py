#!/usr/bin/env python3
"""Regenerate the search-engine and AI-crawler content of the site.

The projects and technologies sections are rendered by JavaScript, which most AI
crawlers do not run. This script writes, from assets/json/projects.json and
assets/json/technologies.json:

  - a plain-HTML copy of both lists inside <noscript> in index.html,
  - the schema.org structured data (JSON-LD) in index.html,
  - llms.txt, a plain-text summary of the site for AI tools,
  - sitemap.xml, listing every public page of the site.

Run it after any change to the site:  python3 scripts/build_seo.py
Check that the generated files are up to date (used in CI):  python3 scripts/build_seo.py --check
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://chakerkhachlek.github.io/"
INDEX = ROOT / "index.html"
MONTHS = "janfebmaraprmayjunjulaugsepoctnovdec"

PERSON = {
    "@type": "Person",
    "@id": SITE + "#person",
    "name": "Chaker Khachlek",
    "jobTitle": "Backend Software Engineer",
    "description": "Backend software engineer and web developer in Paris, specialised in PHP, Symfony and "
                   "real-time web applications. Creator of Loasis and Open Prompt Registry.",
    "url": SITE,
    "image": SITE + "assets/img/photo_portfolio.png",
    "email": "mailto:chaker.khachlek@gmail.com",
    "address": {"@type": "PostalAddress", "addressLocality": "Paris", "addressCountry": "FR"},
    "sameAs": ["https://www.linkedin.com/in/chaker-khachlek/", "https://github.com/ChakerKhachlek"],
}


def date_key(project):
    """Same order as the page: by the end of the date, year then month when given."""
    date = project.get("date", "")
    years = re.findall(r"\d{4}", date) or ["0"]
    month = re.search(r"([A-Za-z]{3})[a-z]*\.?\s+\d{4}\s*$", date)
    index = MONTHS.find(month.group(1).lower()) // 3 + 1 if month else 0
    return int(years[-1]) * 13 + index


def ordered_projects():
    projects = json.loads((ROOT / "assets/json/projects.json").read_text(encoding="utf-8"))
    by_date = sorted(projects, key=date_key, reverse=True)
    return [p for p in by_date if p.get("featured")] + [p for p in by_date if not p.get("featured")]


def technologies():
    return json.loads((ROOT / "assets/json/technologies.json").read_text(encoding="utf-8"))


def tech_list(project):
    return [t.strip() for t in project.get("technologies", "").split(",") if t.strip()]


def absolute(url):
    """Site-relative image paths (assets/...) become full URLs for the JSON-LD."""
    return url if not url or url.startswith("http") else SITE + url


def ai_note(project):
    """' AI-assisted (Claude).' for a project built with AI help, else ''."""
    tools = project.get("ai_assisted") or []
    return f" AI-assisted ({', '.join(tools)})." if tools else ""


def end_year(project):
    years = re.findall(r"\d{4}", project.get("date", ""))
    return years[-1] if years else None


def json_ld(projects, techs):
    items = []
    for i, p in enumerate(projects, 1):
        work = {
            "@type": "CreativeWork",
            "name": p["title"],
            "description": p.get("tagline") or p["description"],
            "creator": {"@id": PERSON["@id"]},
            "keywords": ", ".join(tech_list(p)),
            "image": absolute(p.get("img_link")),
        }
        if end_year(p):
            work["dateCreated"] = end_year(p)
        if p.get("links"):
            work["url"] = p["links"][0]["url"]
        items.append({"@type": "ListItem", "position": i, "item": work})
    person = dict(PERSON, knowsAbout=[t["title"] for t in techs])
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Chaker Khachlek",
             "publisher": {"@id": PERSON["@id"]}},
            {"@type": "ProfilePage", "@id": SITE + "#profile", "url": SITE,
             "name": "Chaker Khachlek — Backend Software Engineer & Web Developer",
             "isPartOf": {"@id": SITE + "#website"}, "mainEntity": {"@id": PERSON["@id"]}},
            person,
            {"@type": "ItemList", "@id": SITE + "#projects", "name": "Projects by Chaker Khachlek",
             "itemListElement": items},
        ],
    }
    body = json.dumps(graph, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'    <script type="application/ld+json">\n{body}\n    </script>\n'


def e(text):
    return html.escape(text, quote=True)


def projects_noscript(projects):
    rows = []
    for p in projects:
        links = "".join(f' <a href="{e(l["url"])}">{e(l["label"])}</a>' for l in p.get("links", []))
        rows.append(
            f'                        <li><strong>{e(p["title"])}</strong> ({e(p.get("date", ""))}): '
            f'{e(p["description"])} <em>Technologies: {e(", ".join(tech_list(p)))}.</em>{e(ai_note(p))}{links}</li>'
        )
    return ("                <noscript>\n                    <ul class=\"seo-static\">\n"
            + "\n".join(rows) + "\n                    </ul>\n                </noscript>\n")


def technologies_noscript(techs):
    groups = {}
    for t in techs:
        groups.setdefault(t.get("category", "Other"), []).append(t["title"])
    rows = [f"                        <li><strong>{e(c)}:</strong> {e(', '.join(names))}</li>"
            for c, names in groups.items()]
    return ("                <noscript>\n                    <ul class=\"seo-static\">\n"
            + "\n".join(rows) + "\n                    </ul>\n                </noscript>\n")


def llms_txt(projects, techs):
    lines = [
        "# Chaker Khachlek",
        "",
        "> Backend software engineer and web developer based in Paris, France. Works on PHP, Symfony, "
        "Ibexa and Shopware projects with AI-assisted workflows, and builds real-time web products: "
        "Loasis, a multiplayer browser game, and Open Prompt Registry, a platform for managing AI prompts.",
        "",
        "## Links",
        "",
        f"- [Portfolio]({SITE})",
        f"- [CV (English and French)]({SITE}cv.html)",
        f"- [Plain-text resume]({SITE}cv-ats.html)",
        "- [LinkedIn](https://www.linkedin.com/in/chaker-khachlek/)",
        "- [GitHub](https://github.com/ChakerKhachlek)",
        "- Email: chaker.khachlek@gmail.com",
        "",
        "## Projects",
        "",
    ]
    for p in projects:
        url = p["links"][0]["url"] if p.get("links") else SITE + "#projects"
        lines.append(f"- [{p['title']}]({url}) ({p.get('date', '')}): {p['description']} "
                     f"Technologies: {', '.join(tech_list(p))}.{ai_note(p)}")
    groups = {}
    for t in techs:
        groups.setdefault(t.get("category", "Other"), []).append(t["title"])
    lines += ["", "## Skills", ""] + [f"- {c}: {', '.join(n)}" for c, n in groups.items()]
    return "\n".join(lines) + "\n"


def sitemap():
    """Every public HTML page; 404 pages and files under scripts/ are left out."""
    pages = sorted(
        p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.html")
        if p.name != "404.html" and not p.relative_to(ROOT).parts[0].startswith((".", "scripts"))
    )
    urls = [SITE + ("" if p == "index.html" else p) for p in pages]
    rows = "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def missing_tags():
    """Every public page needs a title, a meta description and a canonical address."""
    problems = []
    for loc in re.findall(r"<loc>(.*?)</loc>", sitemap()):
        rel = loc[len(SITE):] or "index.html"
        text = (ROOT / rel).read_text(encoding="utf-8")
        for label, pattern in [("<title>", r"<title>[^<]+</title>"),
                               ("meta description", r'<meta name="description" content="[^"]+"'),
                               ("canonical link", r'<link rel="canonical" href="[^"]+"')]:
            if not re.search(pattern, text):
                problems.append(f"{rel}: missing {label}")
    return problems


def replace_block(text, name, content):
    """Replace everything between <!-- seo:NAME:start --> and <!-- seo:NAME:end -->."""
    pattern = re.compile(rf"(<!-- seo:{name}:start[^>]*-->\n)(.*?)(\s*<!-- seo:{name}:end -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"Marker seo:{name} not found in index.html")
    return pattern.sub(lambda m: m.group(1) + content.rstrip("\n") + m.group(3), text, count=1)


def main():
    check = "--check" in sys.argv[1:]
    projects, techs = ordered_projects(), technologies()
    page = INDEX.read_text(encoding="utf-8")
    page = replace_block(page, "jsonld", json_ld(projects, techs))
    page = replace_block(page, "projects", projects_noscript(projects))
    page = replace_block(page, "technologies", technologies_noscript(techs))
    outputs = {INDEX: page, ROOT / "llms.txt": llms_txt(projects, techs), ROOT / "sitemap.xml": sitemap()}

    stale = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if check:
        problems = missing_tags()
        for problem in problems:
            print(problem)
        if stale:
            names = ", ".join(p.relative_to(ROOT).as_posix() for p in stale)
            print(f"SEO/GEO content is out of date in: {names}\nRun: python3 scripts/build_seo.py")
            sys.exit(1)
        if problems:
            sys.exit(1)
        print("SEO/GEO content is up to date.")
        return
    for p in stale:
        p.write_text(outputs[p], encoding="utf-8")
    print(f"{len(projects)} projects, {len(techs)} technologies, {sitemap().count('<loc>')} pages in the sitemap. "
          f"Updated: {', '.join(p.relative_to(ROOT).as_posix() for p in stale) or 'nothing (already up to date)'}.")


if __name__ == "__main__":
    main()
