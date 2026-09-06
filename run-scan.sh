#!/bin/bash

echo "Starting CleanCloud scan..."

mkdir -p reports

cleancloud scan \
  --provider aws \
  --profile cleancloud \
  --all-regions \
  --output json \
  --output-file reports/findings.json

if [ $? -ne 0 ]; then
    echo "CleanCloud scan failed."
    exit 1
fi

echo "Scan completed successfully."
echo "Generating CSV report..."

python scripts/generate_report.py

echo "Reports generated:"
echo "  reports/findings.json"
echo "  reports/aws-cloud-hygiene-report.csv"
