# Release Checklist

Quick reference for creating releases.

## Prerequisites (One-Time Setup)

- [x] Install tools: `brew install git-cliff gh`
- [x] Authenticate GitHub CLI: `gh auth login`
- [x] Add `PYPI_API_TOKEN` to GitHub repository secrets

## Creating a Release

### Option 1: Use Make Commands (Recommended)

```bash
make release-patch  # 0.1.0 → 0.1.1
make release-minor  # 0.1.0 → 0.2.0
make release-major  # 0.1.0 → 1.0.0
```

### Option 2: Use Script Directly

```bash
./scripts/release.sh patch
./scripts/release.sh minor
./scripts/release.sh major
```

### Option 3: Dry Run First

```bash
./scripts/release.sh patch --dry-run  # Preview without committing
```

## What Happens Automatically

When you run a release command:

1. ✅ Version bumped in `pyproject.toml`
2. ✅ CHANGELOG.md generated/updated
3. ✅ Changes committed
4. ✅ Git tag created
5. ✅ Pushed to GitHub
6. ✅ Distribution built
7. ✅ GitHub Release created with:
   - Release notes from CHANGELOG
   - .whl and .tar.gz files
8. ✅ GitHub Actions publishes to PyPI

## Monitoring

- GitHub Actions: https://github.com/irvingpop/honeycomb-api-python/actions
- PyPI Package: https://pypi.org/project/honeycomb-api/
- GitHub Releases: https://github.com/irvingpop/honeycomb-api-python/releases

## Commit Message Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

These messages determine what appears in the CHANGELOG.

## Troubleshooting

See [.claude/docs/RELEASING.md](../.claude/docs/RELEASING.md) for detailed troubleshooting.

Quick fixes:

```bash
# Undo before push (script will ask for confirmation first)
git reset --hard HEAD~1
git tag -d vX.Y.Z

# Check CI locally
make ci

# Update changelog manually
make changelog
```

## Full Documentation

See [.claude/docs/RELEASING.md](../.claude/docs/RELEASING.md) for complete release documentation.
