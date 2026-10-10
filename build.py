"""Build the site from local Markdown and BibTeX. Run with uv run python build.py."""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse, unquote, urlencode
from html.parser import HTMLParser

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from pybtex.database import parse_string
from pybtex.richtext import Text

ROOT = Path(__file__).resolve().parent
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
LINK_FIELDS = {'html': 'HTML', 'pdf': 'PDF', 'doi': 'DOI', 'arxiv': 'arXiv',
               'code': 'Code', 'poster': 'Poster', 'slides': 'Slides',
               'supp': 'Supp', 'website': 'Website', 'blog': 'Blog'}


def front_matter(text: str) -> tuple[dict, str]:
    """Also accepts the empty front matter in the original BibTeX files."""
    match = re.match(r'\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)', text, re.S)
    if text.startswith('---\n---\n'):
        return {}, text[8:]
    if not match:
        return {}, text
    data = yaml.safe_load(match[1]) or {}
    if not isinstance(data, dict):
        raise ValueError('Front matter must be a YAML mapping')
    return data, text[match.end():]


def plain(value: str) -> str:
    return Text.from_latex(value).render_as('text')


def safe_slug(value: str) -> str:
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise ValueError(f'Invalid slug: {value!r}; use lowercase words separated by hyphens')
    return value


def date_value(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value)[:10])


def read_markdown(path: Path) -> dict:
    data, body = front_matter(path.read_text(encoding='utf-8'))
    if not data.get('title'):
        raise ValueError(f'{path.name}: missing title')
    data['body'] = markdown.markdown(body, extensions=['extra', 'toc', 'sane_lists'])
    return data


def post_pages(root: Path, include_drafts: bool, excluded: list[str] = ()) -> list[dict]:
    posts = []
    for path in sorted((root / '_posts').glob('*.md')):
        if path.name in excluded:
            continue
        post = read_markdown(path)
        if post.get('draft') and not include_drafts:
            continue
        match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})-(.+)', path.stem)
        slug = safe_slug(str(post.get('slug') or (match[2] if match else path.stem)))
        if not post.get('date') and not match:
            raise ValueError(f'{path.name}: supply date or use YYYY-MM-DD-slug.md')
        post.update(date=date_value(post.get('date') or match[1]),
                    url=f'/blog/{slug}/', kind='post')
        post.setdefault('description', '')
        post.setdefault('draft', False)
        posts.append(post)
    return sorted(posts, key=lambda p: (p['date'], p['url']), reverse=True)


def bibliography(root: Path, name: str) -> list[dict]:
    _, text = front_matter((root / '_bibliography' / f'{name}.bib').read_text(encoding='utf-8'))
    db = parse_string(text, 'bibtex')
    coauthors = yaml.safe_load((root / '_data/coauthors.yml').read_text()) or {}
    entries = []
    for key, entry in db.entries.items():
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            raise ValueError(f'Unsafe bibliography key: {key}')
        fields = {k: plain(v) for k, v in entry.fields.items()}
        if not fields.get('title') or not fields.get('year'):
            raise ValueError(f'{key}: title and year are required')
        for optional in ('talktype', 'awards', 'abstract'):
            fields.setdefault(optional, '')
        authors = []
        for person in entry.persons.get('author', []):
            last = plain(' '.join(person.prelast_names + person.last_names))
            first = plain(' '.join(person.first_names + person.middle_names))
            full_name = f'{last}, {first}' if first else last
            if person.lineage_names:
                full_name += ', ' + plain(' '.join(person.lineage_names))
            url = next((c['url'] for c in coauthors.get(last, []) if first in c['firstname']), '')
            authors.append({'name': full_name, 'self': last == 'Farrington' and first in ['Joe', 'Joseph', 'J.'], 'url': url})
        links = []
        for field, label in LINK_FIELDS.items():
            if not fields.get(field):
                continue
            value = fields[field]
            if field == 'doi':
                value = 'https://doi.org/' + re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value, flags=re.I)
            elif field == 'arxiv':
                value = value if value.startswith('https://') else 'https://arxiv.org/abs/' + value
            elif field in {'pdf', 'slides', 'poster', 'supp'} and not urlparse(value).scheme and not value.startswith('/'):
                value = '/assets/pdf/' + value
            if urlparse(value).scheme not in {'', 'https', 'http', 'mailto'}:
                raise ValueError(f'{key}: unsupported link scheme in {field}')
            links.append((label, value))
        raw_month = fields.get('month', '')
        month = next((m for m in MONTHS if raw_month.lower() in {m.lower(), m[:3].lower()}), raw_month)
        entries.append({'key': key, 'title': fields['title'], 'year': int(fields['year']),
                        'month': month, 'authors': authors, 'fields': fields,
                        'venue': fields.get('journal', fields.get('booktitle', '')), 'links': links,
                        'scholar': 'https://scholar.google.com/scholar?' + urlencode({'q': '"' + fields['title'] + '"'})})
    return entries


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls, self.ids, self.resources = [], set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.urls.append(attrs[key])
        if tag in {'script', 'img', 'iframe', 'source', 'video', 'audio'} and attrs.get('src'):
            self.resources.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in {'stylesheet', 'icon'}:
            self.resources.append(attrs.get('href', ''))


def check_output(output: Path):
    """Check generated local links, fragment targets, and remote rendering resources."""
    parsed = {}
    for path in output.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text(encoding='utf-8'))
        parsed[path.resolve()] = parser
    for path, page in parsed.items():
        for resource in page.resources:
            if urlparse(resource).scheme in {'http', 'https'} or resource.startswith('//'):
                raise ValueError(f'{path.name}: external rendering resource {resource}')
        for link in page.urls:
            url = urlparse(link)
            if url.scheme or url.netloc:
                continue
            target = (output / unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent / unquote(url.path)) if url.path else path
            target = target.resolve()
            if not target.is_relative_to(output.resolve()):
                raise ValueError(f'Link escapes output: {link}')
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                raise ValueError(f'{path.name}: missing local target {link}')
            if url.fragment and target in parsed and unquote(url.fragment) not in parsed[target].ids:
                raise ValueError(f'{path.name}: missing fragment {link}')


def build(root: Path = ROOT, include_drafts: bool = False) -> Path:
    site = yaml.safe_load((root / 'site.yml').read_text())
    site['url'] = site['url'].rstrip('/')
    posts = post_pages(root, include_drafts, site.get('exclude_posts', []))
    nav = [('About', '/'), ('Papers', '/publications/'), ('Talks', '/talks/')]
    if posts:
        nav.append(('Blog', '/blog/'))
    socials = []
    for link in site['social']:
        if not link.get('url'):
            continue
        svg = (root / 'static/icons' / f"{link['icon']}.svg").read_text()
        # Accessible name is on the enclosing link, avoiding repeated announcements.
        svg = svg.replace('<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
        socials.append({**link, 'svg': svg})
    env = Environment(loader=FileSystemLoader(root / 'templates'), autoescape=True, undefined=StrictUndefined)
    env.globals.update(site=site, nav=nav, posts=posts, socials=socials)
    pages = []
    for path in sorted((root / '_pages').glob('*.md')):
        page = read_markdown(path)
        page.update(url=page['permalink'], kind='page')
        for key in ('description', 'subtitle', 'bibliography'):
            page.setdefault(key, '')
        pages.append(page)
    entries = {name: bibliography(root, name) for name in ('papers', 'talks')}
    staging = root / '_site_build'
    output = root / '_site'
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    written = set()

    def write(url, content):
        if not url.startswith('/') or '..' in url.split('/') or '\\' in url:
            raise ValueError(f'Invalid output path: {url}')
        relative = url.lstrip('/') + ('index.html' if url.endswith('/') else '')
        if relative in written or (staging / relative).exists():
            raise ValueError(f'Duplicate output path: {url}')
        written.add(relative)
        target = staging / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    try:
        shutil.copytree(root / 'static', staging / 'static')
        for page in pages:
            write(page['url'], env.get_template('page.html').render(page=page, bibliography=entries.get(page['bibliography'], [])))
        for post in posts:
            write(post['url'], env.get_template('post.html').render(page=post))
        if posts:
            page = dict(title='Blog', description='Notes and articles by Joe Farrington.', url='/blog/', kind='page')
            write('/blog/', env.get_template('blog.html').render(page=page))
            rss = ET.Element('rss', version='2.0')
            channel = ET.SubElement(rss, 'channel')
            for key, value in [('title', site['name']), ('link', site['url'] + '/blog/'), ('description', site['description'])]:
                ET.SubElement(channel, key).text = value
            for post in posts:
                if post['draft']:
                    continue
                item = ET.SubElement(channel, 'item')
                url = site['url'] + post['url']
                for key, value in [('title', post['title']), ('link', url), ('guid', url), ('description', post['description']),
                                   ('pubDate', post['date'].strftime('%a, %d %b %Y 00:00:00 GMT'))]:
                    ET.SubElement(item, key).text = value
            write('/feed.xml', ET.tostring(rss, encoding='unicode', xml_declaration=True))
        page = dict(title='Page not found', description='', url='/404.html', kind='page')
        write('/404.html', env.get_template('404.html').render(page=page))
        sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        for page in pages + [p for p in posts if not p['draft']]:
            ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = site['url'] + page['url']
        if any(not p['draft'] for p in posts):
            ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = site['url'] + '/blog/'
        write('/sitemap.xml', ET.tostring(sitemap, encoding='unicode', xml_declaration=True))
        write('/robots.txt', f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
        write('/.nojekyll', '')
        # Copy only assets referenced by output, retaining unused template assets in source.
        for html in staging.rglob('*.html'):
            links = Links()
            links.feed(html.read_text(encoding='utf-8'))
            for link in links.urls:
                asset = urlparse(link)
                if asset.scheme or asset.netloc or not asset.path.startswith('/assets/'):
                    continue
                relative = unquote(asset.path.lstrip('/'))
                source = (root / relative).resolve()
                target = (staging / relative).resolve()
                if not source.is_relative_to((root / 'assets').resolve()) or not target.is_relative_to(staging.resolve()):
                    raise ValueError(f'Unsafe asset path: {link}')
                if target.exists():
                    continue
                if not source.is_file():
                    raise ValueError(f'Missing source asset: {link}')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        check_output(staging)
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
    except Exception:
        shutil.rmtree(staging)
        raise
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-drafts', action='store_true', help='Include draft posts for local preview only')
    args = parser.parse_args()
    try:
        result = build(include_drafts=args.include_drafts)
        print(f'Built and checked {result}')
    except (ValueError, OSError) as exc:
        sys.exit(f'Build failed: {exc}')
