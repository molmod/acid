#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Extract the release notes of the acidic package from acidic/CHANGELOG.md into notes.md.

The tag (acidic-vX.Y.Z) is taken from GITHUB_REF and the repository from GITHUB_REPOSITORY.
Both are set by the GitHub Actions runner.
"""

import os
import re
import sys
from pathlib import Path

prefix = "refs/tags/acidic-v"
ref = os.environ["GITHUB_REF"]
is_release = ref.startswith(prefix)
version = ref.removeprefix(prefix) if is_release else "Unreleased"

# Notes are the body of the changelog section "## [version] ..." up to the next "## ".
changelog = Path("acidic/CHANGELOG.md").read_text()
pattern = rf"^## \[{re.escape(version)}\].*\n(.*?)(?=^## |\Z)"
match = re.search(pattern, changelog, re.DOTALL | re.MULTILINE)
notes = match.group(1).strip() if match else ""

# A release must have notes. Without a tag, the notes are not used and may be empty.
if is_release and not notes:
    sys.exit(
        f"No release notes found for version {version} in acidic/CHANGELOG.md.\n"
        f"Rename the section '## [Unreleased]' to '## [{version}] - YYYY-MM-DD'."
    )

url = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/blob/main/acidic/CHANGELOG.md"
link = f"See [acidic/CHANGELOG.md]({url}) for more details."
Path("notes.md").write_text(f"{notes}\n\n{link}\n" if notes else f"{link}\n")
