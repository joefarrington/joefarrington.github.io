import hashlib
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import build
from urllib.parse import urlparse, parse_qs


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ['_pages', '_bibliography', '_data', 'templates', 'static']:
            shutil.copytree(build.ROOT / name, self.root / name)
        (self.root / '_posts').mkdir()
        shutil.copyfile(build.ROOT / 'site.yml', self.root / 'site.yml')

    def post(self, name='2026-10-10-test.md', extra='', body='Hello **world**.'):
        (self.root / '_posts' / name).write_text(f'---\ntitle: Test post\n{extra}---\n\n{body}', encoding='utf-8')

    def test_real_content_and_scholar_links(self):
        output = build.build(self.root)
        papers = (output / 'publications/index.html').read_text()
        talks = (output / 'talks/index.html').read_text()
        self.assertEqual(papers.count('<article class="entry"'), 7)
        self.assertEqual(talks.count('<article class="entry"'), 11)
        self.assertIn('Gallivan award', talks)
        self.assertIn('September', talks)
        self.assertIn('González-Gonzalo', papers)
        self.assertIn('Sánchez', papers)
        self.assertIn('bhHUyBgAAAAJ', papers)
        self.assertNotIn('doi.org/https', papers)
        self.assertFalse((output / 'blog').exists())
        self.assertFalse((output / 'projects').exists())
        self.assertFalse((output / 'news').exists())
        self.assertNotIn('>Blog</a>', (output / 'index.html').read_text())
        self.assertNotIn('class="badge"', papers + talks)
        self.assertNotIn('>BibTeX</a>', papers + talks)
        self.assertFalse((output / 'assets/bib').exists())
        self.assertEqual(papers.count('>Google Scholar</a>'), 8)  # page link plus 7 entries
        entries = build.bibliography(self.root, 'papers')
        for entry in entries:
            query = parse_qs(urlparse(entry['scholar']).query)
            self.assertEqual(query['q'], ['"' + entry['title'] + '"'])
        self.assertIn('HTML</a>', papers)
        self.assertIn('PDF</a>', papers)
        build.check_output(output)

    def test_blog_and_draft_preview(self):
        self.post(extra='description: A summary\n')
        self.post('2026-10-11-draft.md', extra='draft: true\n')
        output = build.build(self.root)
        self.assertTrue((output / 'blog/test/index.html').exists())
        self.assertFalse((output / 'blog/draft').exists())
        self.assertIn('>Blog</a>', (output / 'index.html').read_text())
        feed = ET.parse(output / 'feed.xml')
        self.assertEqual(len(feed.findall('./channel/item')), 1)
        self.assertIn('<strong>world</strong>', (output / 'blog/test/index.html').read_text())
        output = build.build(self.root, include_drafts=True)
        self.assertIn('Draft preview', (output / 'blog/draft/index.html').read_text())
        self.assertEqual(len(ET.parse(output / 'feed.xml').findall('./channel/item')), 1)
        self.assertNotIn('/blog/draft/', (output / 'sitemap.xml').read_text())
        output = build.build(self.root)
        self.assertFalse((output / 'blog/draft').exists())

    def test_post_date_override_and_slug(self):
        self.post(extra='date: 2025-01-02\nslug: renamed\n')
        posts = build.post_pages(self.root, False)
        self.assertEqual(posts[0]['date'].isoformat(), '2025-01-02')
        self.assertEqual(posts[0]['url'], '/blog/renamed/')

    def test_duplicate_and_unsafe_slugs(self):
        self.post(extra='slug: same\n')
        self.post('2026-10-11-second.md', extra='slug: same\n')
        with self.assertRaisesRegex(ValueError, 'Duplicate output'):
            build.build(self.root)
        self.post(extra='slug: ../outside\n')
        with self.assertRaisesRegex(ValueError, 'Invalid slug'):
            build.build(self.root)

    def test_failed_build_preserves_previous_output(self):
        output = build.build(self.root)
        before = (output / 'index.html').read_bytes()
        self.post(body='![Missing](/assets/img/missing.png)')
        with self.assertRaisesRegex(ValueError, 'Missing source asset'):
            build.build(self.root)
        self.assertEqual(before, (output / 'index.html').read_bytes())

    def test_used_assets_only(self):
        assets = self.root / 'assets'
        assets.mkdir()
        (assets / 'notes.txt').write_text('Referenced download')
        (assets / 'unused.txt').write_text('Unused template material')
        self.post(body='[Notes](/assets/notes.txt)')
        output = build.build(self.root)
        self.assertTrue((output / 'assets/notes.txt').exists())
        self.assertFalse((output / 'assets/unused.txt').exists())

    def test_external_rendering_dependency_rejected(self):
        self.post(body='![Remote](https://example.com/image.jpg)')
        with self.assertRaisesRegex(ValueError, 'external rendering resource'):
            build.build(self.root)

    def test_broken_fragment_rejected(self):
        self.post(body='[Missing](#not-here)')
        with self.assertRaisesRegex(ValueError, 'missing fragment'):
            build.build(self.root)

    def test_bibtex_edge_cases(self):
        (self.root / '_bibliography/talks.bib').write_text('''---
---
@string{venue = "A venue"}
@article{talk, title={Example}, journal=venue, month={{July}}, year={2026},
 talktype={Poster}, awards={An award}, doi={10.1000/example}}
''')
        entries = build.bibliography(self.root, 'talks')
        self.assertEqual(entries[0]['month'], 'July')
        self.assertEqual(entries[0]['venue'], 'A venue')
        self.assertEqual(entries[0]['authors'], [])
        self.assertIn(('DOI', 'https://doi.org/10.1000/example'), entries[0]['links'])

    def test_template_examples_excluded(self):
        name = '2015-10-20-comments.md'
        shutil.copyfile(build.ROOT / '_posts' / name, self.root / '_posts' / name)
        output = build.build(self.root)
        self.assertFalse((output / 'blog').exists())

    def test_optional_portrait_and_profile_links(self):
        config = build.yaml.safe_load((self.root / 'site.yml').read_text())
        config['portrait'] = {'path': '/assets/img/portrait.svg', 'alt': 'Joe portrait'}
        next(link for link in config['social'] if link['icon'] == 'mezzanine')['url'] = 'https://example.org/profile'
        (self.root / 'site.yml').write_text(build.yaml.safe_dump(config))
        assets = self.root / 'assets/img'
        assets.mkdir(parents=True)
        (assets / 'portrait.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        output = build.build(self.root)
        html = (output / 'index.html').read_text()
        self.assertIn('alt="Joe portrait"', html)
        self.assertIn('aria-label="Mezzanine"', html)
        self.assertNotIn('aria-label="Letterboxd"', html)
        self.assertTrue((output / 'assets/img/portrait.svg').exists())

    def test_workflow_deployment_is_main_only(self):
        workflow = build.yaml.load((build.ROOT / '.github/workflows/deploy.yml').read_text(), Loader=build.yaml.BaseLoader)
        self.assertEqual(workflow['on']['push']['branches'], ['main'])
        self.assertEqual(workflow['on']['pull_request']['branches'], ['main'])
        self.assertEqual(workflow['jobs']['deploy']['needs'], 'build')
        self.assertIn("github.event_name == 'push'", workflow['jobs']['deploy']['if'])
        self.assertNotIn('--include-drafts', str(workflow))
        self.assertEqual(workflow['jobs']['deploy']['permissions']['pages'], 'write')
        self.assertEqual(workflow['permissions']['contents'], 'read')

    def test_reproducible_build(self):
        def hashes(path):
            return {str(p.relative_to(path)): hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
        first = hashes(build.build(self.root))
        second = hashes(build.build(self.root))
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
