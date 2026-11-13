#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0
set -e

# Settings
# Keep PYTHON_VERSION consistent with requires-python in pyproject.toml.
PYTHON_VERSION=3.14.10
# Keep UV_VERSION consistent with the uv-pre-commit rev in .pre-commit-config.yaml
# and with the build system in acidic/pyproject.toml.
UV_VERSION=0.13.7
TYPST_VERSION=0.15.1

# Platform-specific settings
# Update the checksums of all platforms when changing UV_VERSION or TYPST_VERSION.
# Keep the platforms consistent with required-environments in pyproject.toml.
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    # Static builds, which work on any x86_64 Linux system
    TARGET=x86_64-unknown-linux-musl
    UV_SHA256=287491da03f2a785c70fa75b13e1f849918c2f2b5415fe84876b8214eeb792f9
    TYPST_SHA256=a6d077d0a95eed5a2eba715b2dae06be954f624ccbf85758a03f389ded33118c
    SHA256SUM=(sha256sum)
    ;;
  Darwin-arm64)
    TARGET=aarch64-apple-darwin
    UV_SHA256=81b811b57e4624df7ed3aac148e0359100d9962f3d9dce00aec533dc2e086731
    TYPST_SHA256=48f62ed034aa3a7978309579ac6ca00045e2ef0da73114e8af27cfd8e74dc05a
    SHA256SUM=(shasum -a 256)
    ;;
  *)
    echo "Unsupported platform: $(uname -s) $(uname -m)" >&2
    echo "Only x86_64 Linux and arm64 macOS (Apple Silicon) are supported." >&2
    exit 1
    ;;
esac

# Keep the uv cache and the Python installation inside .venv.
# Absolute paths make this work from any subdirectory.
export UV_CACHE_DIR=$PWD/.venv/cache
export UV_PYTHON_INSTALL_DIR=$PWD/.venv/uv-python

# Install uv
mkdir -p .venv/bin/
UV_NAME=uv-$TARGET
UV_ARCHIVE=.venv/$UV_NAME-$UV_VERSION.tar.gz
curl -LsSf -o $UV_ARCHIVE \
  https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$UV_NAME.tar.gz
echo "$UV_SHA256  $UV_ARCHIVE" | "${SHA256SUM[@]}" --check --quiet
tar -xf $UV_ARCHIVE -C .venv/bin --strip-components=1 $UV_NAME/uv $UV_NAME/uvx
rm $UV_ARCHIVE

# Install venv in the same .venv directory
.venv/bin/uv venv --allow-existing --python=$PYTHON_VERSION --managed-python

# Install the exact package versions from uv.lock
.venv/bin/uv sync --locked

# Install typst (not available on PyPI as a standalone executable)
TYPST_NAME=typst-$TARGET
TYPST_ARCHIVE=.venv/$TYPST_NAME-v$TYPST_VERSION.tar.xz
curl -LsSf -o $TYPST_ARCHIVE \
  https://github.com/typst/typst/releases/download/v$TYPST_VERSION/$TYPST_NAME.tar.xz
echo "$TYPST_SHA256  $TYPST_ARCHIVE" | "${SHA256SUM[@]}" --check --quiet
tar -xf $TYPST_ARCHIVE -C .venv/bin --strip-components=1 $TYPST_NAME/typst
rm $TYPST_ARCHIVE

# Create the shell.sh script
# The workflows are located in subdirectories of the project root.
# STEPUP_PATH_FILTER makes StepUp track files in the project root
# (e.g. the editable install of acidic/), except for the virtual environment.
# TYPST_IGNORE_SYSTEM_FONTS makes Typst use only its built-in fonts,
# so the documents do not depend on the fonts installed on the system.
cat > shell.sh << EOF
#!/usr/bin/env bash
export PYTHONNOUSERSITE=1
export PROJECT_ROOT=$PWD
source $PWD/.venv/bin/activate
export STEPUP_PATH_FILTER='-../.venv:+../'
export TYPST_IGNORE_SYSTEM_FONTS=true
export UV_CACHE_DIR=$UV_CACHE_DIR
export UV_PYTHON_INSTALL_DIR=$UV_PYTHON_INSTALL_DIR
$SHELL -i
EOF
# The .envrc file is shell.sh without the first and the last line.
sed '1d;$d' shell.sh > .envrc
chmod +x shell.sh

# Create the module file for HPC clusters (also works locally)
mkdir -p .venv/modules
cat > .venv/modules/acid.lua << EOF
local project_root = "$PWD"
setenv("PYTHONNOUSERSITE", "1")
setenv("PROJECT_ROOT", project_root)
local venv = project_root .. "/.venv"
setenv("STEPUP_PATH_FILTER", "-../.venv:+../")
setenv("TYPST_IGNORE_SYSTEM_FONTS", "true")
setenv("VIRTUAL_ENV", venv)
setenv("UV_CACHE_DIR", venv .. "/cache")
setenv("UV_PYTHON_INSTALL_DIR", venv .. "/uv-python")
prepend_path("PATH", venv .. "/bin")
EOF
