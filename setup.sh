#!/usr/bin/env bash
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0
set -e

# Settings
PYTHON_VERSION=3.14
TYPST_VERSION=0.15.1
TYPST_SHA256=a6d077d0a95eed5a2eba715b2dae06be954f624ccbf85758a03f389ded33118c

# Bootstrap uv
mkdir -p .venv/bin/
curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL=".venv/bin" sh

# Install venv in the same .venv directory
export UV_PYTHON_INSTALL_DIR=.venv/uv-python
.venv/bin/uv venv --allow-existing --python=$PYTHON_VERSION --managed-python

# Install the exact package versions from uv.lock
.venv/bin/uv sync --locked

# Install typst (not available on PyPI as a standalone executable)
TYPST_NAME=typst-x86_64-unknown-linux-musl
TYPST_ARCHIVE=.venv/$TYPST_NAME-v$TYPST_VERSION.tar.xz
curl -LsSf -o $TYPST_ARCHIVE \
  https://github.com/typst/typst/releases/download/v$TYPST_VERSION/$TYPST_NAME.tar.xz
echo "$TYPST_SHA256  $TYPST_ARCHIVE" | sha256sum --check --quiet
tar -xf $TYPST_ARCHIVE -C .venv/bin --strip-components=1 $TYPST_NAME/typst
rm $TYPST_ARCHIVE

# Create the shell.sh script
# The workflows are located in subdirectories of the project root.
# STEPUP_PATH_FILTER makes StepUp track files in the project root (e.g. lib/),
# except for the virtual environment.
cat > shell.sh << EOF
#!/usr/bin/env bash
export PYTHONNOUSERSITE=1
export PROJECT_ROOT=$PWD
source $PWD/.venv/bin/activate
export PYTHONPATH=$PWD/lib
export STEPUP_PATH_FILTER='-../.venv:+../'
$SHELL -i
EOF
head -n-1 shell.sh | tail -n+2 > .envrc
chmod +x shell.sh

# Create the module file for HPC clusters (also works locally)
mkdir -p .venv/modules
cat > .venv/modules/acid.lua << EOF
local project_root = "$PWD"
setenv("PYTHONNOUSERSITE", "1")
setenv("PROJECT_ROOT", project_root)
local venv = project_root .. "/.venv"
setenv("STEPUP_PATH_FILTER", "-../.venv:+../")
setenv("VIRTUAL_ENV", venv)
prepend_path("PYTHONPATH", venv .. "/lib/python$PYTHON_VERSION/site-packages")
prepend_path("PYTHONPATH", project_root .. "/lib")
prepend_path("PATH", venv .. "/bin")
EOF
