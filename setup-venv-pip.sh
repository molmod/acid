#!/usr/bin/env bash
set -e

if [[ -v VSC_ARCH_LOCAL ]]; then
    # Configure VSC Python
    module load Python/3.12.3-GCCcore-13.3.0
    ARCHDIR="${VSC_ARCH_LOCAL}${VSC_ARCH_SUFFIX}"
fi

# If you want to install with a Python version that is not your OS's default:
# PYTHON3=/usr/bin/python3.11 ./setup-venv-pip.sh
: "${PYTHON3:=$(which python3)}"

# This script assumes you have a running and somewhat modern Python environment.
${PYTHON3} -c 'import sys; assert sys.version_info.major == 3; assert sys.version_info.minor >= 11'

echo "Create the venv and activation script"
if [[ -v VSC_ARCH_LOCAL ]]; then
    ${PYTHON3} -m venv venvs/${ARCHDIR}
    # Create an activate script
    cat > activate << 'EOF'
export SOURCE_DATE_EPOCH=315532800
export REPREP_LATEX=pdflatex
export TEXMFHOME="${PWD}/texmf"
module load Python/3.12.3-GCCcore-13.3.0 git-lfs
ARCHDIR="${VSC_ARCH_LOCAL}${VSC_ARCH_SUFFIX}"
source ${PWD}/venvs/${ARCHDIR}/bin/activate
export XDG_CACHE_HOME="${PWD}/venvs/cache"
EOF
    chmod +x activate
    source activate

else
    ${PYTHON3} -m venv venv
    # Create an .envrc for direnv.
    cat > .envrc << 'EOF'
export SOURCE_DATE_EPOCH=315532800
export REPREP_LATEX=pdflatex
export TEXMFHOME="${PWD}/texmf"
source ${PWD}/venv/bin/activate
export XDG_CACHE_HOME="${PWD}/venv/cache"
EOF
    direnv allow
    eval "$(direnv export bash)"

fi

# Activate and update installer tools
# See https://github.com/jazzband/pip-tools/issues/2176
python3 -m pip install -U 'pip<25.1' pip-tools

# Install requirements
python3 -m piptools compile -q
python3 -m piptools sync

# Intall typst
(
    cd ${XDG_CACHE_HOME}
    wget -nc https://github.com/typst/typst/releases/download/v0.13.1/typst-x86_64-unknown-linux-musl.tar.xz
    tar -xf typst-x86_64-unknown-linux-musl.tar.xz
    install typst-x86_64-unknown-linux-musl/typst ${VIRTUAL_ENV}/bin
)
