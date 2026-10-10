# Self-contained site replacement plan

## Agreed scope

Inspected commit: `3b02b81fb09ba56172eda2b07f71198457ead05e`.
Branch: `codex/self-contained-site`.
The replacement is implemented on this branch. Deployment of the replacement
remains pending review and merge; see `MIGRATION.md` for repository settings.

Replace the three main pages, preserving their current routes:

- Homepage: `/`, authored in `_pages/about.md`.
- Papers: `/publications/`, authored in `_pages/publications.md` and
  `_bibliography/papers.bib` (7 records).
- Talks: `/talks/`, authored in `_pages/talks.md` and
  `_bibliography/talks.bib` (11 records).

The user identifies the existing posts, projects, and news as inherited template
examples rather than content to migrate. Exclude those examples and their
assets from the replacement output; their historical routes do not need
compatibility or redirects. Their original versions remain in Git history.
Do not build a Liquid compatibility layer or migrate Distill examples.

Provide the ability to add real blog posts by creating new Markdown files.
Preserve the homepage's general structure and social links. Support adding a
local portrait and editing the homepage later; no photo has been supplied yet.

## Inspected baseline

The repository uses Jekyll/al-folio, Ruby plugins, Sass, and a GitHub Actions
workflow that also installs Mermaid CLI through npm. Templates load Bootstrap,
MDB, icon fonts, Google Fonts, syntax styles, MathJax, and other scripts from
external services. A Ruby plugin fetches a template Medium feed during builds.
None of that template infrastructure is needed for the agreed scope.

The existing bibliography template renders titles, authors, venue, date,
abbreviations, links, and talk-specific metadata. Keep that recognizable layout
and its HTML/PDF buttons rather than replacing it with generic citations.

## Simple Python approach

Use a small Python static-site builder with four direct dependencies:
Python-Markdown, Jinja2, PyYAML, and Pybtex for BibTeX and structured names.
Manage dependencies and the Python environment with `uv`, using
`pyproject.toml` and a committed `uv.lock`. Resolve compatible versions during
implementation and use the lockfile for reproducible installs. Avoid custom BibTeX
parsing, a plugin framework, or a general citation-style engine.

No Ruby, Node, Sass compiler, frontend framework, database, or live server is
needed. Generate ordinary HTML and local assets into `_site/` for GitHub Pages.
Use plain responsive CSS, system fonts, and local inline SVG social icons.
JavaScript is optional and limited to useful small enhancements.

Replace the Twitter bird with Font Awesome's `x-twitter` brand SVG and use
`https://x.com/joe_farrington` with an accessible label such as "X (Twitter)".
Keep the other recognizable social/academic icons, using locally stored SVGs
from Font Awesome and Academicons as appropriate. Match their visual size,
color, spacing, and alignment in CSS; do not load whole icon fonts or CDN
stylesheets. Retain icon license/attribution notices. No wholesale icon-set
replacement is needed just to support X.
Source: https://github.com/FortAwesome/Font-Awesome/blob/6.x/svgs/brands/x-twitter.svg


```text
build.py
pyproject.toml
uv.lock
site.yml                  # identity, social links, optional portrait
_pages/                   # homepage, publications, talks as Markdown
_posts/                   # real future posts only; initially empty
_bibliography/            # papers.bib and talks.bib stay authoritative
_data/coauthors.yml       # preserve existing author link metadata
templates/                # base, page, bibliography, post, blog index
static/                   # CSS, icons, optional small script
assets/                   # retained real assets and future portrait/downloads
_site/                    # generated and ignored
```

Author workflow:

```sh
uv sync --locked
uv run --locked python build.py
uv run --locked python -m http.server 8000 --directory _site
```

## Homepage and Markdown pages

Keep homepage copy in Markdown and retain its Research, Background, and Open
source software structure. Keep the current social destinations from
`_config.yml`, including email, GitHub, LinkedIn, Scholar, ORCID, Twitter, and
ResearchGate. Store active links in a short, understandable `site.yml`.
The existing Scholar link is `https://scholar.google.com/citations?user=bhHUyBgAAAAJ`;
retain it in the social links and add a clearly labeled Google Scholar link
on the Publications page.

Provide optional portrait settings (local image path and meaningful alt text)
and a responsive layout that works with or without a photo. Keep the overall
academic style, readable widths, and existing main navigation. Later copy and
photo changes can be made without editing templates.

Support YAML front matter, embedded HTML, tables, fenced code, footnotes, and
heading IDs. Publications and Talks remain Markdown pages with an optional
introductory body. Replace their Liquid loops/bibliography tags with a simple
front-matter bibliography selector; templates render the entries below the
page body. Derive year headings from BibTeX instead of maintaining year lists.

## Personal profile links

Support optional Letterboxd and Mezzanine profile links alongside the existing
social links, and Goodreads later. Only render a link when its profile URL is
configured; the user's Letterboxd and Mezzanine URLs are still needed.
Font Awesome provides Letterboxd and Goodreads brand icons. For Mezzanine,
use the custom three-tone greyscale `static/icons/mezzanine.svg`, based on the app
icon’s overlapping spotlight/stage silhouette, with an accessible Mezzanine
label. A size preview is in `previews/mezzanine-icon.svg`. Keep assets
local and apply the same size, color, and spacing as other social links.
Do not add feeds or account integrations; these are outbound profile links.

Sources:
- https://fontawesome.com/icons/letterboxd
- https://fontawesome.com/icons/brands/solid/goodreads
- https://www.theaterdiary.com/press/

## Papers and talks

Preserve both `.bib` files and all 18 entries. Strip the existing empty YAML
front-matter wrapper before parsing. Keep keys as HTML anchors and retain
custom fields in the source. Handle Unicode authors, name particles, nested
braces, string definitions, and talks with no author field.

Preserve the current presentation:

- Year groups in descending order, with stable entry ordering within a year.
- Title, authors, venue, and month/year, without abbreviation badges.
- Emphasis on Joe/Joseph Farrington and existing coauthor links.
- HTML and PDF links styled as compact buttons; retain support for code,
  poster, slides, supplement, website, and other populated link fields.
- Talk type and awards on the talks page.
- Optional abstract disclosure using native `<details>` when enabled.

Keep one HTML button, using the DOI URL when available and falling back to
the HTML field. Do not show a separate DOI button; keep PDF separate.
Accept bare or full-URL DOIs without duplicating the DOI prefix. Local PDF and
slide paths resolve under the retained assets directory. Outbound links to
papers and third-party PDFs remain outbound links; they need not be downloaded.
Do not rewrite bibliographic content or impose a new citation style.

Add a Google Scholar button for each paper using a search for its quoted title.
Visitors can use Scholar’s Cite feature to export BibTeX. Do not generate local
BibTeX downloads. The authoritative BibTeX sources remain unchanged.

## Future Markdown blog

Start with an empty `_posts/` directory and no template example posts in the
output. Hide the Blog navigation item until at least one published post exists.
Generate `/blog/` and `/blog/<slug>/` when real posts are added. No old blog
route migration, archive system, pagination, projects, or news features are
required for this initial version.

Document this minimal authoring example in README (do not publish it as a post):

```markdown
---
title: My first post
date: 2026-10-10
description: A short optional summary.
---

Write ordinary Markdown here.
```

Use a filename such as `_posts/2026-10-10-my-first-post.md`; derive the slug
from the filename and permit an explicit `slug` override. Read the date from
front matter, falling back to the filename. Support `draft: true`, excluded
from normal builds. Sort the blog index by date descending. Use the shared
navigation, typography, and footer on articles. Include title, date, description,
canonical metadata, and an RSS feed. Reject duplicate or invalid output paths
with a clear error.

Local preview is the review workflow before committing, pushing, or merging.
Normal `uv run --locked python build.py` previews the production output; an explicit
`uv run --locked python build.py --include-drafts` includes draft posts for local review.
GitHub CI and deployment always use the normal build, excluding drafts.
Local draft builds require no hosted preview service.

Math rendering, advanced citations, tag archives, and other blog features can
be added when real posts need them; they do not justify dependencies now.

## Self-contained output

All styling, icons, and any scripts required to render the site are local.
The build does not fetch feeds or GitHub metadata. Remove external fonts,
Disqus, analytics, CDN scripts, and inherited demo integrations. Retain normal
external research and social hyperlinks. Produce 404, robots.txt, sitemap,
canonical URLs, and `.nojekyll` alongside the pages.

## Implementation sequence

1. Preserve the three main page sources, all BibTeX entries, and social/coauthor
   destinations; remove template examples from the active replacement sources.
2. Add Python configuration, Markdown/front-matter parsing, BibTeX parsing,
   templates, and local asset copying. Render the three main routes.
3. Style the homepage and bibliography to retain their current structure and
   link buttons; add optional portrait support and accessible mobile navigation.
4. Add the minimal Markdown blog pipeline, draft handling, blog index, and feed.
5. Rename the repository default branch from `master` to `main` as part of
   the migration. Update the GitHub default branch, local tracking configuration,
   affected open pull request targets, and any branch protection/ruleset or
   documentation references as needed. Coordinate the rename with workflow
   changes so deployment remains functional.
6. Replace the template `.github/workflows/deploy.yml` with a Python workflow
   using `uv` and `uv sync --locked`; run builds and checks with `uv run --locked`.
   Build/check pull requests targeting `main` without deployment; build and
   deploy on pushes to `main` (including merges). Use GitHub’s official Pages artifact upload/deploy actions, changing the
   repository Pages source to GitHub Actions. Retain `gh-pages` as historical
   output; it is not the new publishing source. Give deployment write permissions only to the deployment
   job, and deploy only after checks succeed. Do not rename the remote branch
   or publish this branch as part of planning.
7. Remove obsolete theme tooling and unused demo assets. Document setup,
   preview, homepage/photo edits, new papers/talks, and new posts in README.

## Quick-start README

Replace the current short README as part of implementation with concise,
copyable instructions matching the finished builder:

1. **Local setup:** installing `uv` on Windows and Bash/WSL, cloning, the
   supported Python version, and `uv sync --locked`. Explain that `uv` manages
   `.venv` and can install the required Python version; manual activation and
   pip commands are unnecessary.
2. **Build and preview:** `uv run --locked python build.py`, then
   `uv run --locked python -m http.server 8000 --directory _site`; open
   `http://localhost:8000`. Explain that changes require rebuilding and refreshing
   the browser, and show how to stop the server.
3. **Add a paper:** edit `_bibliography/papers.bib`; provide a minimal example
   with a unique key, title, author, venue, year, and optional DOI/HTML/PDF fields.
   Explain automatic year grouping and per-paper Google Scholar links.
4. **Add a talk:** edit `_bibliography/talks.bib`; provide a minimal example
   showing title, venue, month/year, `talktype`, and optional awards/slides/poster
   fields. Explain that author is optional for talks.
5. **Add a blog post:** create `_posts/YYYY-MM-DD-slug.md`; show YAML front
   matter and Markdown body, optional description and slug override, and the
   resulting URL. Explain when the Blog navigation appears.
6. **Preview drafts:** use `draft: true` and
   `uv run --locked python build.py --include-drafts` for local review; run a normal build to
   restore production output. Drafts are excluded by CI/deployment.
7. **Edit homepage/photo:** identify the Markdown source and optional local
   portrait path/alt text in `site.yml`, plus social link configuration.
8. **Publish:** review locally, commit, and push/merge to `main`; the Python
   GitHub Action builds and deploys. Point to the Actions run for build errors.

Keep this a quick reference with small examples rather than a long tutorial.
Verify commands against the implementation; do not document unfinished
commands as working features. Keep setup tooling limited to `uv` and Git, with Python managed through `uv`.

## Acceptance checks

- `/`, `/publications/`, and `/talks/` render; all 7 papers and 11 talks appear
  with intact keys, text, awards, and HTML/PDF destinations.
- Each paper has a Google Scholar link with its quoted title as the search
  query. The page-level Scholar link matches the existing profile.
- Main navigation, social links, coauthor links, anchors, and local downloads
  resolve. No example posts/projects/news appear in the generated site.
- Homepage works with and without a local portrait, at mobile/desktop widths,
  and with keyboard navigation and visible focus.
- Add a temporary Markdown post and verify its page, index, feed, and Blog link;
  verify default draft exclusion and explicit local inclusion. Remove the
  temporary fixture from the published output.
- GitHub default branch and local tracking use `main`; affected protection
  rules and PR targets are checked after the rename.
- Workflow checks PRs targeting `main` without publishing, deploys successful
  pushes to `main`, and never uses the include-drafts option.
- Focused parser/build tests cover nested-brace months, Unicode names, absent
  talk authors, DOI forms, date fallback/override, and duplicate output paths.
- Commit `uv.lock` and verify setup/build with `uv sync --locked` and
  `uv run --locked`. Build is reproducible and does not require network access
  after installing dependencies. Generated pages make no third-party rendering requests.
- README covers setup, papers, talks, posts, drafts, homepage/photo changes,
  and publishing with copyable examples. Python setup, build, and preview
  instructions work on Windows and WSL.

## Current execution limitation

The default sandbox runner fails before starting a shell. Approved execution
outside the sandbox works and was used to clone, create the branch, and inspect
source. No app settings were changed.

## Implementation decisions

- Automated Scholar import was discussed and explicitly deferred by the user.
- Keep template files in source for reference, exclude inherited posts through
  `site.yml`, and copy only referenced assets. The active build has no Ruby/Node
  dependencies. Broad cleanup was rejected by automatic approval review.
- Use official GitHub Pages artifact deployment instead of branch-push
  deployment; this avoids token-trigger limitations and generated commits.
