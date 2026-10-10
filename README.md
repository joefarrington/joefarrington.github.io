# Joe Farrington's website

A self-contained static site built with Python, Markdown, Jinja2, and BibTeX.
Dependencies and the environment are managed by **uv**. No Ruby, Node, frontend
framework, or database is needed. The output has no external font/script/CDN
dependencies; research and profile links still open their original websites.

## Quick setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git.
Use the same commands in PowerShell or Bash/WSL:

```sh
git clone https://github.com/joefarrington/joefarrington.github.io.git
cd joefarrington.github.io
uv sync --locked
```

`uv` creates `.venv` and installs Python 3.12 if needed. No environment activation
is required. Commit `pyproject.toml` and `uv.lock` together when dependencies change.

## Build and preview locally

```sh
uv run --locked python build.py
uv run --locked python -m http.server 8000 --directory _site
```

Open [localhost:8000](http://localhost:8000). After editing, rebuild in another
terminal and refresh the browser. Stop the server with **Ctrl+C**. `_site/` is
regenerated output; edit the sources instead. A failed build leaves the last
successful output intact.

## Add a paper

Add an entry to `_bibliography/papers.bib`, using a unique citation key:

```bibtex
@article{farrington2026example,
  title   = {An example paper},
  author  = {Farrington, Joseph and Other, Alex},
  journal = {Journal Name},
  year    = {2026},
  doi     = {10.1234/example},
  html    = {https://example.org/article},
  pdf     = {https://example.org/article.pdf}
}
```

The page groups entries by year automatically, preserving source order within
each year. `doi`, `html`, and `pdf` are optional. The citation key becomes
the entry's anchor; keep existing keys stable. A Google Scholar button searches
for each paper's quoted title, where visitors can use Cite to export BibTeX.
Abbreviation badges and local BibTeX downloads are not displayed.

Optional link fields: `code`, `poster`, `slides`, `supp`, `website`, `blog`, `arxiv`.
For local PDFs, put a file under `assets/pdf/` and use `pdf = {filename.pdf}`.
Authors use standard BibTeX `Last, First and Last, First` syntax.

## Add a talk

Add an entry to `_bibliography/talks.bib`:

```bibtex
@article{Farrington2026Conference,
  title    = {An example talk},
  journal  = {Conference Name},
  month    = {July},
  year     = {2026},
  talktype = {Oral},
  slides   = {https://example.org/slides.pdf}
}
```

`author` is optional for talks. Add `awards = {Award description}` if applicable.
Other optional links work as for papers. Rebuild to see the new entry.

## Add a blog post

Create `_posts/2026-10-10-my-first-post.md`:

```markdown
---
title: My first post
date: 2026-10-10
description: A short optional summary.
---

Write ordinary Markdown here.

![An image](/assets/img/example.jpg)
```

Put referenced images in `assets/img/`. Only referenced assets are copied to the
output. Use root-relative asset links (`/assets/...`). Tables, fenced code,
footnotes, heading links, and embedded HTML are supported.

The post URL is `/blog/my-first-post/`; an optional `slug` overrides the filename
slug. Use lowercase words separated by hyphens. The date falls back to the
filename when omitted. The Blog link and RSS feed appear when a post is published.
Posts are listed newest first. Avoid changing a published slug without arranging
a redirect. Remote embedded images/scripts are rejected to keep rendering local.

The inherited example posts are explicitly excluded in `site.yml` and remain in
Git for reference. Do not reuse their filenames for real posts. Old projects,
news, Liquid templates, and Ruby tooling are also ignored by the Python builder.

## Preview drafts

Add `draft: true` to the post's front matter, then run:

```sh
uv run --locked python build.py --include-drafts
```

View it with the same local server. Drafts are marked in the preview and omitted
from RSS/sitemap. Restore the production output with a normal build:

```sh
uv run --locked python build.py
```

CI and deployment never use `--include-drafts`. No hosted preview service is needed.

## Edit the homepage, photo, or social links

Edit `_pages/about.md` for homepage text. To add a portrait, put an image under
`assets/img/` and update `site.yml`:

```yaml
portrait:
  path: /assets/img/portrait.jpg
  alt: Joe Farrington
```

Leave `path` empty to omit it. The CSS shows a square crop. Social links are also
in `site.yml`; add your Letterboxd, Mezzanine, or Goodreads URL to show that icon.
Empty URLs hide the link. SVG sources/licenses are in `static/icons/`.

Papers and Talks page titles/descriptions and optional introductory Markdown
live in `_pages/publications.md` and `_pages/talks.md`. Their permalinks stay
`/publications/` and `/talks/`.

## Check and publish

```sh
uv run --locked python -m unittest discover -s tests -v
uv run --locked python build.py
```

The build checks local links, image/download paths, fragment links, output-path
collisions, and external rendering resources. Review the local preview, commit,
and push/merge to **main**. `.github/workflows/deploy.yml` tests and builds with
`uv`, then deploys the `_site/` artifact directly to **GitHub Pages** only after
successful checks. Pull
requests targeting `main` run checks without publishing. Check the repository's
**Actions** tab if a build fails. GitHub Pages must use **Settings → Pages → Source → GitHub Actions**.
The old `gh-pages` branch is retained as deployment history; the new workflow
does not write generated commits to it.

Until the replacement is reviewed and merged, it lives on
`codex/self-contained-site`; do not merge merely to preview it. Branch migration
status is recorded in `MIGRATION.md`.
