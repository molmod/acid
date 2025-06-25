#!/usr/bin/env bash
if [ -z "$1" ]; then
    echo "Error: Remote host argument missing."
    exit 1
fi
rm -rf upload
mkdir -p upload
cp -a \
  acid-dataset/output/*.csv \
  validation-stacie-report/figures/*.* \
  validation-stacie-report/tables/*.* \
  upload/
rsync -P -crp upload/ --delete ${1}:projects/emd-viscosity/acid-test/
rm -rf upload
