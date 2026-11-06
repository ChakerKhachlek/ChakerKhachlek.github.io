# Portfolio of Chaker Khachlek

Static GitHub Pages site served at https://chakerkhachlek.github.io/ (Bootstrap, Alpine.js,
no build step). Projects and technologies come from `assets/json/projects.json` and
`assets/json/technologies.json` and are rendered in the browser.

## Rule: update SEO/GEO with every change to the website

Any change to the site (content, projects, technologies, pages, CV) must ship with its SEO/GEO
update in the same change. This is automated, but still do it locally before committing:

1. Run `python3 scripts/build_seo.py`. It regenerates from the JSON data the `<noscript>`
   copies of the projects and technologies lists in `index.html` (for crawlers that don't run
   JavaScript), the schema.org JSON-LD, `llms.txt` and `sitemap.xml`. Never edit the
   `<!-- seo:... -->` blocks, `llms.txt` or `sitemap.xml` by hand.
2. Run `python3 scripts/build_seo.py --check`; it must print "SEO/GEO content is up to date".
   The "SEO/GEO update" GitHub workflow runs the script on every push, commits any regenerated
   files back to the branch, republishes the site when that happens on `main`, and fails if a
   page is missing its title, description or canonical link. Pull before pushing again after
   it has committed.
3. A new page needs a `<title>`, a `<meta name="description">`, a
   `<link rel="canonical" href="https://chakerkhachlek.github.io/...">`, the Google Analytics
   tag (`G-8K4Z6ZJ7WC`) and the favicon links. The check enforces the first three.
4. If the bio, role or contact details change, update them in `index.html` (About, hero,
   `<meta name="description">`, Open Graph tags) and in `PERSON` and `llms_txt()` in
   `scripts/build_seo.py`, then rerun the script.
5. If `cv.html` or `cv-ats.html` change, regenerate the four PDFs in `assets/pdf/` so they
   match the pages.
6. When `css/style.css` changes, bump the `?v=` on its `<link>` in `index.html` so browsers
   don't keep a cached copy.

## Other notes

- Keep image `alt` text on every `<img>`.
- The old https://chakerkhachlek.github.io/CKPortfolio/ addresses are redirects served from the
  CKPortfolio repository; this repository is the live site.
