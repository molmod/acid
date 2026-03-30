#!/usr/bin/env bash
# SPDX-FileCopyrightText: © 2026 ACID Contributors <https://doi.org/10.5281/zenodo.15722902>
# SPDX-License-Identifier: CC-BY-SA-4.0
#SBATCH --job-name=setup
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=1:00:00
#SBATCH --mem=5G
set -e

# If VSC_HOME is set, load the appropriate Python module
if [[ -n "${VSC_HOME}" ]]; then
    module load Python/3.13.1-GCCcore-14.2.0
fi

# If you want to install with a Python version that is not your OS's default:
# PYTHON3=/usr/bin/python3.11 ./setup-venv-pip.sh
: "${PYTHON3:=$(which python3)}"

# This script assumes you have a running and somewhat modern Python environment.
${PYTHON3} -c 'import sys; assert sys.version_info.major == 3; assert sys.version_info.minor >= 11'

${PYTHON3} -m venv venv

# Create an activation script.
# This script is named .loadvenv to avoid confusion with the standard activate script.
rm -f .loadvenv

if [[ -n "${VSC_HOME}" ]]; then
    echo 'module load Python/3.13.1-GCCcore-14.2.0' >> .loadvenv
fi

cat >> .loadvenv << 'EOF'
export SOURCE_DATE_EPOCH=315532800
source ${PWD}/venv/bin/activate
export PATH=$(realpath ${PWD}/1_dataset/scripts/):${PATH}
export PYTHONPATH=$(realpath ${PWD}/1_dataset/lib/):${PYTHONPATH}
EOF

# Load the environment and update installer tools
source ./.loadvenv
# See https://github.com/jazzband/pip-tools/issues/2176
python3 -m pip install -U pip==26.0.1 pip-tools==7.5.3

# Install requirements
python3 -m piptools compile
python3 -m piptools sync

# Install typst
TYPST_VERSION=v0.14.2
TYPST_URL=https://github.com/typst/typst/releases/download/${TYPST_VERSION}/typst-x86_64-unknown-linux-musl.tar.xz
TYPST_CACHE=${XDG_CACHE_HOME:-${HOME}/.cache}/typst-${TYPST_VERSION}-x86_64-unknown-linux-musl.tar.xz
wget -nc -O ${TYPST_CACHE} ${TYPST_URL} || true
tar -xf ${TYPST_CACHE} -C ${VIRTUAL_ENV}/bin typst-x86_64-unknown-linux-musl/typst --strip-components=1
chmod +x ${VIRTUAL_ENV}/bin/typst
