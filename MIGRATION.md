# Migration status

- Renamed GitHub's default branch from `master` to `main` and updated local
  `main` tracking and `origin/HEAD`.
- No branch protection rules, repository rulesets, or open PRs required migration
  at inspection time. The existing `github-pages` environment had no branch filter.
- Changed GitHub Pages source from `gh-pages` branch publishing to **GitHub Actions**.
  The existing deployed website remains available until the new workflow deploys.
- The replacement workflow tests and builds pull requests to `main`. Only pushes
  to `main` deploy the built artifact with GitHub's official Pages actions.
- Replacement source is on `codex/self-contained-site`; review and merge to publish.
- Original BibTeX sources are unchanged. The eight inherited posts are excluded
  by filename in `site.yml`; project/news/legacy templates are ignored by the builder.
  Legacy files and unused demo assets remain in Git for reference and are not
  copied to output. Their former routes are outside the migration scope.
- Automated Google Scholar import is deferred. Add/edit papers in BibTeX manually.
- Letterboxd, Mezzanine, and Goodreads URLs are empty pending the owner's profiles.
  Portrait is optional and currently unset.
- Default sandbox execution fails in this session; approved execution outside
  the sandbox works. No app settings were changed.

For other existing checkouts after the branch rename:

```sh
git branch -m master main
git fetch origin
git branch --set-upstream-to=origin/main main
git remote set-head origin -a
```

Only run the rename in a checkout that still has a local `master` branch.

## Validation

- Python unit/integration tests cover bibliography preservation and valid downloads,
  drafts/blog/RSS, routing, referenced assets, link failures, portrait/profile
  configuration, workflow guards, and repeatable builds.
- Local HTTP checks returned 200 for the three main pages, CSS, and a BibTeX download.
- No browser engine is available in the execution runtime, so visual desktop/mobile
  inspection and a native Windows smoke test remain to be performed by the owner.
