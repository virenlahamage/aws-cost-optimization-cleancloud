import csv
import json
from pathlib import Path


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input and output files
INPUT_FILE = PROJECT_ROOT / "reports" / "findings.json"
OUTPUT_FILE = PROJECT_ROOT / "reports" / "aws-cloud-hygiene-report.csv"


def get_recommendation(finding):
    details = finding.get("details", {})
    resource_type = finding.get("resource_type", "").lower()
    title = finding.get("title", "").lower()

    if resource_type == "security_group" or "security group" in title:
        referenced = details.get("referenced_by_other_sg", False)

        if referenced:
            return (
                "Validate security group references and Terraform/application "
                "dependencies before removal."
            )

        return (
            "Validate ENIs, applications, Terraform dependencies, and other "
            "references before removal."
        )

    if resource_type == "s3_bucket" or "s3" in resource_type:
        return (
            "Review bucket purpose and apply appropriate tags. "
            "Do not delete based on this finding alone."
        )

    return "Review the finding and validate dependencies before remediation."


def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return 1

    try:
        with INPUT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON file: {exc}")
        return 1

    findings = data.get("findings", [])

    columns = [
        "Region",
        "Resource Type",
        "Resource ID",
        "Resource Name",
        "Finding",
        "Risk",
        "Confidence",
        "Attached ENIs",
        "Referenced by Other SG",
        "VPC ID",
        "Age (days)",
        "Estimated Monthly Cost (USD)",
        "Tags",
        "Recommendation",
        "Detected At",
    ]

    rows = []

    for finding in findings:
        details = finding.get("details") or {}
        tags = details.get("tags") or {}

        resource_name = (
            details.get("sg_name")
            or details.get("name")
            or details.get("bucket_name")
            or ""
        )

        rows.append(
            {
                "Region": finding.get("region", ""),
                "Resource Type": finding.get("resource_type", ""),
                "Resource ID": finding.get("resource_id", ""),
                "Resource Name": resource_name,
                "Finding": finding.get("title", ""),
                "Risk": finding.get("risk", ""),
                "Confidence": finding.get("confidence", ""),
                "Attached ENIs": details.get("attached_eni_count", ""),
                "Referenced by Other SG": details.get(
                    "referenced_by_other_sg", ""
                ),
                "VPC ID": details.get("vpc_id", ""),
                "Age (days)": details.get("age_days", ""),
                "Estimated Monthly Cost (USD)": details.get(
                    "estimated_monthly_cost_usd", ""
                ),
                "Tags": "; ".join(
                    f"{key}={value}" for key, value in tags.items()
                ),
                "Recommendation": get_recommendation(finding),
                "Detected At": finding.get("detected_at", ""),
            }
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV report generated successfully: {OUTPUT_FILE}")
    print(f"Total findings exported: {len(rows)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
