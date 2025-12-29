# Release Process

This document describes how to release new versions of the honeycomb-api package to PyPI.

## Prerequisites

### One-Time Setup

1. **Required Tools**:
   - `poetry` - Python dependency management
   - `git-cliff` - Changelog generation: `brew install git-cliff`
   - `gh` - GitHub CLI: `brew install gh`

2. **PyPI Account**: Ensure you have a PyPI account with access to the `honeycomb-api` package

3. **GitHub Secret**: Add your PyPI API token to GitHub repository secrets
   - Go to: Repository Settings → Secrets and variables → Actions
   - Create a new secret named `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starts with `pypi-`)

4. **GitHub CLI Authentication**:
   ```bash
   gh auth login
   ```

5. **GitHub Environment** (Optional but recommended):
   - Go to: Repository Settings → Environments
   - Create environment named `pypi`
   - Add protection rules (e.g., require approval for production releases)

## Release Workflow

The release process is fully automated via the `scripts/release.sh` script and Makefile commands.

### Quick Start

```bash
# For patch releases (0.1.0 → 0.1.1)
make release-patch

# For minor releases (0.1.0 → 0.2.0)
make release-minor

# For major releases (0.1.0 → 1.0.0)
make release-major
```

### What Happens Automatically

The release script will:
1. ✅ Check for uncommitted changes (fails if any)
2. ✅ Bump version in `pyproject.toml`
3. ✅ Generate/update `CHANGELOG.md` using git-cliff
4. ✅ Extract release notes for the new version
5. ✅ Show you a preview of changes and release notes
6. ✅ Commit changes with message `chore(release): bump version to X.Y.Z`
7. ✅ Create annotated git tag `vX.Y.Z`
8. ✅ Push commit and tag to GitHub
9. ✅ Build distribution packages (wheel + sdist)
10. ✅ Create GitHub Release with:
    - Release notes extracted from changelog
    - Distribution files attached as assets

### After the Script Runs

The GitHub Actions workflow (`.github/workflows/publish.yml`) automatically:
1. ✅ Verifies tag version matches package version
2. ✅ Verifies CHANGELOG.md has been updated
3. ✅ Runs full CI checks (`make ci`)
4. ✅ Builds the package
5. ✅ Publishes to PyPI

Monitor progress at: https://github.com/irvingpop/honeycomb-api-python/actions

### Dry Run Mode

Test the release process without making changes:

```bash
./scripts/release.sh patch --dry-run
```

This shows you what would happen without committing anything.

## Changelog Generation

The project uses [git-cliff](https://git-cliff.org) to generate changelogs from conventional commits.

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `build`: Build system changes

**Examples**:
```bash
feat(triggers): add support for custom thresholds
fix(queries): handle missing dataset parameter correctly
docs: update installation instructions
chore(release): bump version to 0.2.0
```

### Manual Changelog Update

To regenerate the changelog without creating a release:

```bash
make changelog
```

## Manual Publishing (Emergency Fallback)

If the automated release process fails, you can publish manually:

```bash
# Ensure you're on the correct version
poetry version

# Run CI checks
make ci

# Build
poetry build

# Publish (requires POETRY_PYPI_TOKEN_PYPI or interactive login)
poetry publish

# Manually create GitHub release
gh release create "v$(poetry version -s)" \
  --title "v$(poetry version -s)" \
  --notes "Release notes here" \
  dist/*.whl dist/*.tar.gz
```

## Version Management

### Single Source of Truth

Version is defined in one place: `[tool.poetry].version` in [pyproject.toml:28](../../pyproject.toml#L28)

At runtime, the version is read dynamically:
```python
from honeycomb import __version__
print(__version__)  # Reads from package metadata
```

### Pre-releases

For alpha/beta/rc releases:

```bash
poetry version prerelease  # 0.1.0 → 0.1.1a0
poetry version prerelease  # 0.1.1a0 → 0.1.1a1
```

## Workflow Triggers

The publish workflow (`.github/workflows/publish.yml`) can be triggered:

1. **Automatically**: When a tag starting with `v` is pushed (e.g., `v0.2.0`)
2. **Automatically**: When a GitHub release is published
3. **Manually**: Via GitHub Actions UI (workflow_dispatch)

The release script triggers #1 and #2 automatically.

## Troubleshooting

### Uncommitted Changes

If you see: `Error: You have uncommitted changes`

```bash
# Review changes
git status

# Commit or stash them
git add .
git commit -m "your message"
```

### Tag/Version Mismatch

If the GitHub Actions workflow fails with: `Error: Tag version does not match package version`

The release script should prevent this, but if it happens:

```bash
# Check versions
poetry version -s
git describe --tags

# Fix by updating pyproject.toml and re-running release
```

### CHANGELOG Not Updated

If the workflow fails with: `Error: CHANGELOG.md does not contain entry for version X.Y.Z`

The release script should prevent this, but if it happens:

```bash
# Regenerate changelog
make changelog

# Commit and re-tag
git add CHANGELOG.md
git commit --amend --no-edit
git tag -f -a "vX.Y.Z" -m "Release vX.Y.Z"
git push --force origin main --tags
```

### CI Failures

The workflow runs full CI before publishing. If checks fail:

```bash
# Run locally to debug
make ci

# Fix issues, then create a new release
git add .
git commit -m "fix: issue description"
make release-patch  # Creates new version
```

### PyPI Token Issues

If publishing fails with authentication errors:

1. Verify `PYPI_API_TOKEN` secret exists in GitHub
2. Check token hasn't expired on PyPI
3. Regenerate token if needed

### GitHub CLI Issues

If `gh release create` fails:

```bash
# Check authentication
gh auth status

# Re-authenticate if needed
gh auth login

# Or set token manually
export GH_TOKEN=your_github_token
```

### Undoing a Release (Before Push)

If you need to abort after the script starts:

The script will ask for confirmation before pushing. If you need to undo after that point but before the push completes:

```bash
# Undo the commit
git reset --hard HEAD~1

# Delete the tag
git tag -d vX.Y.Z

# Restore version
git checkout pyproject.toml poetry.lock CHANGELOG.md
```

### Undoing a Release (After Push)

If you need to retract a published release:

```bash
# Delete the GitHub release
gh release delete vX.Y.Z --yes

# Delete the tag locally and remotely
git tag -d vX.Y.Z
git push origin :refs/tags/vX.Y.Z

# Note: You CANNOT unpublish from PyPI
# You can only yank a release (marks it as broken):
# pip install twine
# twine yank honeycomb-api X.Y.Z
```

## Testing Releases

### TestPyPI

For testing the release process without affecting production:

1. Get TestPyPI token from https://test.pypi.org
2. Add as `TEST_PYPI_API_TOKEN` secret
3. Modify workflow to use TestPyPI temporarily
4. Install from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ honeycomb-api
   ```

## Breaking Changes

Until version 1.0.0, breaking changes are acceptable (see [CLAUDE.md:23](../../CLAUDE.md#L23)).

After 1.0.0, follow semantic versioning strictly:
- **Patch** (1.0.x): Bug fixes only
- **Minor** (1.x.0): New features, backward compatible
- **Major** (x.0.0): Breaking changes
