#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0 OR LGPL-3.0-or-later
"""Extract the example local settings from 1_dataset/README.md.

This writes the (only) JSON code block of the README to 1_dataset/local-settings.json,
so the lightrun workflow tests the settings exactly as they are documented.
Run this script from the root of the repository.
"""

import json
import re
from pathlib import Path


def main():
    readme = Path("1_dataset/README.md").read_text()
    blocks = re.findall(r"^```json\n(.*?)^```$", readme, flags=re.DOTALL | re.MULTILINE)
    if len(blocks) != 1:
        raise ValueError(f"Expected exactly one JSON block in the README, found {len(blocks)}.")
    json.loads(blocks[0])  # Fail early if the block is not valid JSON.
    Path("1_dataset/local-settings.json").write_text(blocks[0])


if __name__ == "__main__":
    main()
