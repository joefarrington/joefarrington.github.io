# Joe Farrington's personal website

A self-contained static site built with Python, Markdown, Jinja2, and BibTeX.

## Quick setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git.
Use the same commands in PowerShell or Bash/WSL:

```sh
git clone https://github.com/joefarrington/joefarrington.github.io.git
cd joefarrington.github.io
uv sync --locked
```

If you already have the repository, open a terminal in its folder and run
`uv sync --locked`. `uv` creates `.venv` and installs Python 3.12 if needed;
no environment activation is required.

## Build and preview locally

```sh
uv run --locked python build.py
uv run --locked python -m http.server 8000 --directory _site
```

Open [localhost:8000](http://localhost:8000). After editing, rebuild in another
terminal in the repository folder and refresh the browser. Stop the server with
**Ctrl+C**. `_site/` is generated output; edit the sources instead. A failed build
leaves the last successful output intact.

## Add a paper

Add an entry to `_bibliography/papers.bib`, using a unique citation key:

```bibtex
@article{farrington2026example,
  title   = {An example paper},
  author  = {Farrington, Joseph and Other, Alex},
  journal = {Journal Name},
  year    = {2026},
  doi     = {10.1234/example},
  pdf     = {https://example.org/article.pdf}
}
```

Entries are grouped by year, preserving source order within each year. `title`
and `year` are required. Authors use BibTeX's `Last, First and Last, First` syntax.
Keep existing citation keys stable: they become the entries' URL anchors.

Paper links are optional, apart from the automatically generated Scholar button:

- `doi` supplies the **HTML** link. If there is no DOI, use `html` for the article URL.
- `pdf` supplies a separate **PDF** link. For a local file, put it in `assets/pdf/`
  and use `pdf = {filename.pdf}`.
- `scholar` supplies the **Google Scholar** link. Open the paper on your Scholar
  profile, copy its URL, and add `scholar = {copied URL}`. If omitted, the button
  searches Scholar for the paper's quoted title. Visitors can export BibTeX there.

Other optional link fields are `code`, `poster`, `slides`, `supp`, `website`,
`blog`, and `arxiv`. Rebuild to see the new entry.

## Add a talk

Add an entry to `_bibliography/talks.bib`, using a unique citation key:

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

`title` and `year` are required; `author` is optional. Add
`awards = {Award description}` if applicable. The same optional link fields
work as for papers, except that talks do not display a Scholar button.
For local slides, put the file in `assets/pdf/` and use `slides = {filename.pdf}`.
Rebuild to see the new entry.

## Add a page

Create a Markdown file such as `_pages/teaching.md`:

```markdown
---
title: Teaching
permalink: /teaching/
description: Teaching and supervision.
---

Write ordinary Markdown here.
```

The build discovers the file automatically and creates `/teaching/`. `title`
and `permalink` are required; `description` is optional. Use a unique permalink
with a leading and trailing slash. To show the page in the top navigation, add
`('Teaching', '/teaching/')` to the `nav` list in `build.py`. Rebuild and visit
[localhost:8000/teaching/](http://localhost:8000/teaching/).

## Add a blog post

Create `_posts/2026-10-10-my-first-post.md`:

```markdown
---
title: My first post
date: 2026-10-10
description: A short optional summary.
---

Write ordinary Markdown here.
```

The post URL is `/blog/my-first-post/`; an optional `slug` overrides the filename
slug. Use lowercase words separated by hyphens. The date falls back to the
filename when omitted. Posts are listed newest first, and the Blog navigation
link and RSS feed appear automatically when a post is published. Rebuild to see
changes. Keep published slugs stable unless you also arrange redirects.

Pages and posts support tables, fenced code, footnotes, heading anchors, and
embedded HTML. Put images in `assets/img/` and reference them with Markdown such
as `![Image description](/assets/img/photo.jpg)`. Only referenced files under
`assets/` are copied to the output. Use root-relative asset links (`/assets/...`);
remote embedded images and scripts are rejected to keep rendering local.

## Preview drafts

Add `draft: true` to a post's front matter, then run:

```sh
uv run --locked python build.py --include-drafts
```

View it with the same local server. Drafts are marked in the preview and omitted
from RSS and the sitemap. Restore the production output with a normal build:

```sh
uv run --locked python build.py
```

GitHub Actions builds without `--include-drafts`, so drafts are never published.

## Edit the homepage or social links

Edit `_pages/about.md` for homepage text.

Social links are in `site.yml`; add your Letterboxd, Mezzanine, or Goodreads
URL to show that icon. Empty URLs hide the link. SVG sources and licenses are
in `static/icons/`.

Papers and Talks page titles, descriptions, and optional introductory Markdown
live in `_pages/publications.md` and `_pages/talks.md`. Keep their existing
permalinks to preserve `/publications/` and `/talks/`.

## Check and publish

Run the checks and review the local preview before publishing:

```sh
uv run --locked python -m unittest discover -s tests -v
uv run --locked python build.py
```

The build checks local links, image/download paths, fragment links, output-path
collisions, and external rendering resources. It does not verify external
article or profile URLs.

Commit your changes and push or merge them to `main` to publish.
`.github/workflows/deploy.yml` runs tests and builds the site, then deploys
`_site/` to GitHub Pages after successful checks. Pull requests targeting `main`
run the same checks without publishing. Check the repository's **Actions** tab
if a build fails. GitHub Pages must use **Settings → Pages → Source → GitHub Actions**.

When changing dependencies, commit `pyproject.toml` and `uv.lock` together.

## Repository layout

```text
.github/workflows/deploy.yml   # build/check PRs; deploy main
_pages/                       # homepage, papers, talks, additional pages
_bibliography/                # paper and talk records in BibTeX
_posts/                       # Markdown blog posts
assets/img/                   # your photos and post images
assets/pdf/                   # your PDFs/slides
static/                       # CSS, favicon, local profile icons/licenses
templates/                    # Jinja page and blog templates
tests/                        # builder tests
build.py                      # site generator, navigation, output checks
site.yml                      # identity and profile links
pyproject.toml, uv.lock        # Python dependencies and lockfile
```

## Acknowledgements

This site originally used [al-folio](https://github.com/alshedivat/al-folio).
Its layout informed the current Python-based replacement. The original
copyright notice is retained alongside the notice for Joe Farrington's
contributions in the [MIT license](LICENSE). Third-party icon credits and
licenses are in [static/icons/](static/icons/README.md).
