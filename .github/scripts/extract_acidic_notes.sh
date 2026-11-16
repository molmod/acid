#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: LGPL-3.0-or-later
# Extract the release notes of the acidic package from acidic/CHANGELOG.md into notes.md.
# Usage: .github/scripts/extract_acidic_notes.sh OWNER/SLUG GITREF
set -euo pipefail

IFS='/' read -ra REPOSITORY <<<"${1}"
OWNER=${REPOSITORY[0]}
SLUG=${REPOSITORY[1]}
GITREF=${2}

if [[ "${GITREF}" == refs/tags/acidic-v* ]]; then
    VERSION="${GITREF#refs/tags/acidic-v}"
else
    VERSION="Unreleased"
fi

# Extract the section of the changelog for this version, without the heading.
# The dots in the version are escaped, so they only match literal dots.
sed -n "/^## \[${VERSION//./\\.}\]/, /^## /{ /^##/!p }" acidic/CHANGELOG.md > notes.md

# Remove leading and trailing empty lines.
sed -e :a -e '/./,$!d;/^\n*$/{$d;N;};/\n$/ba' -i notes.md

# A release must have notes. (Without a tag, the notes are not used, so they may be empty.)
if [[ "${VERSION}" != "Unreleased" ]] && ! grep -q '[^[:space:]]' notes.md; then
    echo "No release notes found for version ${VERSION} in acidic/CHANGELOG.md." >&2
    echo "Rename the section '## [Unreleased]' to '## [${VERSION}] - YYYY-MM-DD' (or similar)." >&2
    exit 1
fi

# Add a link to the full changelog, separated by an empty line from the notes (if any).
if [[ -s notes.md ]]; then
    echo >> notes.md
fi
echo "See [acidic/CHANGELOG.md](https://github.com/${OWNER}/${SLUG}/blob/main/acidic/CHANGELOG.md)" \
     "for more details." >> notes.md
