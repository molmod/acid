#!/usr/bin/env bash
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0
set -e

# Settings
# Keep PYTHON_VERSION consistent with requires-python in pyproject.toml.
PYTHON_VERSION=3.14.10
# Keep UV_VERSION consistent with the uv-pre-commit rev in .pre-commit-config.yaml.
UV_VERSION=0.13.7
UV_SHA256=287491da03f2a785c70fa75b13e1f849918c2f2b5415fe84876b8214eeb792f9
TYPST_VERSION=0.15.1
TYPST_SHA256=a6d077d0a95eed5a2eba715b2dae06be954f624ccbf85758a03f389ded33118c

# Keep the uv cache and the Python installation inside .venv.
# Absolute paths make this work from any subdirectory.
export UV_CACHE_DIR=$PWD/.venv/cache
export UV_PYTHON_INSTALL_DIR=$PWD/.venv/uv-python

# Install uv (static build, works on any x86_64 Linux system)
mkdir -p .venv/bin/
UV_NAME=uv-x86_64-unknown-linux-musl
UV_ARCHIVE=.venv/$UV_NAME-$UV_VERSION.tar.gz
curl -LsSf -o $UV_ARCHIVE \
  https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$UV_NAME.tar.gz
echo "$UV_SHA256  $UV_ARCHIVE" | sha256sum --check --quiet
tar -xf $UV_ARCHIVE -C .venv/bin --strip-components=1 $UV_NAME/uv $UV_NAME/uvx
rm $UV_ARCHIVE

# Install venv in the same .venv directory
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
export UV_CACHE_DIR=$UV_CACHE_DIR
export UV_PYTHON_INSTALL_DIR=$UV_PYTHON_INSTALL_DIR
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
setenv("UV_CACHE_DIR", venv .. "/cache")
setenv("UV_PYTHON_INSTALL_DIR", venv .. "/uv-python")
prepend_path("PYTHONPATH", project_root .. "/lib")
prepend_path("PATH", venv .. "/bin")
EOF
