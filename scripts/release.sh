#!/usr/bin/env bash
# Release script - bumps version, generates changelog, and creates GitHub release
set -e

BUMP_TYPE="${1:-patch}"
DRY_RUN="${2:-}"

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(patch|minor|major|prepatch|preminor|premajor|prerelease)$ ]]; then
    echo "Error: Invalid bump type '$BUMP_TYPE'"
    echo "Usage: $0 {patch|minor|major|prepatch|preminor|premajor|prerelease} [--dry-run]"
    exit 1
fi

echo "==> Starting release process (bump: $BUMP_TYPE)"

# Check for required tools
if ! command -v git-cliff &> /dev/null; then
    echo "Error: git-cliff is not installed"
    echo "Install with: brew install git-cliff (macOS)"
    echo "Or see: https://git-cliff.org/docs/installation"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "Error: gh (GitHub CLI) is not installed"
    echo "Install with: brew install gh (macOS)"
    echo "Or see: https://cli.github.com/manual/installation"
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "Error: You have uncommitted changes. Commit or stash them first."
    git status -s
    exit 1
fi

# Ensure we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo "Warning: You're on branch '$CURRENT_BRANCH', not 'main'"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current version
OLD_VERSION=$(poetry version -s)
echo "Current version: $OLD_VERSION"

# Bump version
echo "==> Bumping version ($BUMP_TYPE)"
poetry version "$BUMP_TYPE"
NEW_VERSION=$(poetry version -s)
echo "New version: $NEW_VERSION"

# Generate full changelog
echo "==> Generating changelog"
git-cliff --tag "v${NEW_VERSION}" --output CHANGELOG.md

# Extract release notes for this version only
echo "==> Extracting release notes for v${NEW_VERSION}"
RELEASE_NOTES_FILE=$(mktemp)
git-cliff --tag "v${NEW_VERSION}" --unreleased --strip all > "$RELEASE_NOTES_FILE"

# Show what changed
echo ""
echo "==> Changes to be committed:"
git diff pyproject.toml CHANGELOG.md
echo ""
echo "==> Release notes:"
cat "$RELEASE_NOTES_FILE"

# Confirm
echo ""
if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "Dry run mode - no changes will be committed"
    git checkout pyproject.toml CHANGELOG.md
    rm -f "$RELEASE_NOTES_FILE"
    exit 0
fi

read -p "Commit, tag, and create GitHub release for v${NEW_VERSION}? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting. Rolling back version change..."
    git checkout pyproject.toml CHANGELOG.md
    rm -f "$RELEASE_NOTES_FILE"
    exit 1
fi

# Commit changes
echo "==> Committing release"
git add pyproject.toml poetry.lock CHANGELOG.md
git commit -m "chore(release): bump version to ${NEW_VERSION}"

# Create annotated tag
echo "==> Creating tag v${NEW_VERSION}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

# Push commit and tag
echo "==> Pushing to origin"
git push origin "$CURRENT_BRANCH"
git push origin "v${NEW_VERSION}"

# Build distribution packages
echo "==> Building distribution packages"
poetry build

# Create GitHub release with assets
echo "==> Creating GitHub release"
gh release create "v${NEW_VERSION}" \
    --title "v${NEW_VERSION}" \
    --notes-file "$RELEASE_NOTES_FILE" \
    dist/honeycomb_api-${NEW_VERSION}-py3-none-any.whl \
    dist/honeycomb_api-${NEW_VERSION}.tar.gz

# Cleanup
rm -f "$RELEASE_NOTES_FILE"

echo ""
echo "✅ Release v${NEW_VERSION} published successfully!"
echo ""
echo "View release at:"
gh release view "v${NEW_VERSION}" --web
echo ""
echo "The GitHub Actions workflow will now publish to PyPI automatically."
echo "Monitor at: https://github.com/irvingpop/honeycomb-api-python/actions"
