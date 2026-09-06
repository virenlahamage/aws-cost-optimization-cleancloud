# AWS Cost Optimization & Cloud Hygiene with CleanCloud — Implementation Guide

This document records the implementation of the AWS cloud hygiene and cost-optimization scanning workflow built around CleanCloud.

The implementation uses a dedicated read-only AWS IAM identity, an AWS CLI profile, CleanCloud for AWS resource scanning, and a custom Python reporting script to automatically convert CleanCloud JSON findings into a CSV report.

> **Security note:** The screenshots included in this document were captured during implementation. Before publishing this documentation to a public GitHub repository, review every screenshot and redact credentials, access keys, secret keys, account IDs, client names, bucket names, internal resource names, or other information that should not be public.

---

## 1. Project Objective

The objective of this project is to create a safe and repeatable AWS cloud-hygiene workflow that can:

- Scan AWS resources across active regions
- Detect potential cloud-hygiene issues
- Use a dedicated read-only IAM identity
- Validate AWS permissions before scanning
- Save raw findings as JSON
- Automatically convert JSON findings into CSV
- Make findings easier to review
- Provide a foundation for future remediation and automation

The overall workflow follows:

```text
Detect → Validate → Remediate → Verify → Automate
```

The current implementation focuses on:

```text
Detect → Report
```

Remediation is intentionally separated from the scanner and should only happen after individual findings are validated.

---

# 2. Architecture

The current implementation follows this architecture:

```text
                    AWS Account
                         |
                         v
                Read-Only IAM User
                         |
                         v
                 AWS CLI Profile
                         |
                         v
                 +---------------+
                 |   CleanCloud  |
                 |   AWS Scanner |
                 +-------+-------+
                         |
                         | JSON
                         v
                 reports/findings.json
                         |
                         v
                +--------------------+
                | generate_report.py |
                |    JSON → CSV      |
                +---------+----------+
                          |
                          | CSV
                          v
          reports/aws-cloud-hygiene-report.csv
```

CleanCloud is used as the scanning engine. The project adds the reporting and execution automation around it.

---

# 3. Technology Stack

| Technology | Purpose |
|---|---|
| AWS | Cloud environment being scanned |
| AWS IAM | Access control and least-privilege scanning |
| AWS CLI | AWS authentication and command execution |
| CleanCloud | AWS cloud-hygiene scanner |
| Python | JSON-to-CSV report generation |
| Bash | End-to-end scan automation |
| JSON | Raw scanner output |
| CSV | Human-readable report |
| Git | Version control |
| GitHub | Project repository |

---

# 4. Project Structure

The project is organized as:

```text
aws-cost-optimization-cleancloud/
│
├── README.md
├── cleancloud.yaml
├── run-scan.sh
│
├── iam/
│   └── cleancloud-readonly-policy.json
│
├── scripts/
│   └── generate_report.py
│
├── docs/
│   ├── setup.md
│   ├── architecture.md
│   ├── implementation.md
│   ├── findings.md
│   ├── remediation.md
│   └── screenshots/
│       ├── 01-iam-user.png
│       ├── 02-aws-cli-profile.png
│       ├── 03-cleancloud-installation.png
│       ├── 04-cleancloud-doctor-authentication.png
│       ├── 05-cleancloud-doctor-permissions-1.png
│       ├── 06-cleancloud-doctor-permissions-2.png
│       ├── 07-cleancloud-scan-findings-1.png
│       ├── 08-cleancloud-scan-findings-2.png
│       ├── 09-automated-json-to-csv-report.png
│       └── 10-generated-reports.png
│
└── reports/
    ├── findings.json
    └── aws-cloud-hygiene-report.csv
```

Generated reports may contain account-specific AWS resource information and should normally be excluded from a public repository.

---

# 5. Step 1 — Create a Dedicated AWS IAM Identity

A dedicated IAM identity was created for the CleanCloud scanning process.

The purpose of this identity is to provide CleanCloud with only the permissions required to inspect AWS resources.

The IAM identity has:

- Console access disabled
- Programmatic access configured
- A custom read-only policy attached
- Permissions required for the AWS hygiene checks

The permission model is:

```text
CleanCloud IAM User
        |
        v
cleancloud-hygiene-policy
        |
        +-- EC2 Describe
        +-- EBS Describe
        +-- RDS Describe
        +-- ELB Describe
        +-- S3 Read
        +-- CloudWatch Read
        +-- CloudTrail Read
        +-- OpenSearch Read
        +-- Redshift Read
        +-- STS GetCallerIdentity
```

### Screenshot — IAM User

<img width="1908" height="898" alt="Screenshot 2026-09-06 121252" src="https://github.com/user-attachments/assets/2e4fbd74-5d5f-47ed-aa57-82984f49902b" />


The screenshot shows the dedicated IAM user and the custom managed policy attached directly to the user.

---

# 6. Step 2 — Configure AWS CLI Profile

A separate AWS CLI profile was configured for CleanCloud.

The profile name used in the implementation is:

```text
cleancloud
```

The profile allows the CleanCloud commands to explicitly use the dedicated scanning identity.

The configuration command is:

```bash
aws configure --profile cleancloud
```

The profile configuration contains:

```text
AWS Access Key ID
AWS Secret Access Key
Default Region
Output Format
```

The credentials remain local and must never be committed to GitHub.

### Screenshot — AWS CLI Configuration

<img width="1906" height="1112" alt="Screenshot 2026-09-06 121546" src="https://github.com/user-attachments/assets/ed11939e-e295-4942-80f9-596ed3cb252d" />


> **Important:** This screenshot contains credential-related information. Do not publish this screenshot to a public repository unless all credentials and sensitive information have been completely redacted. If real credentials were exposed, rotate/revoke them before publishing.

---

# 7. Verify AWS Identity

The configured AWS CLI profile can be validated with:

```bash
aws sts get-caller-identity --profile cleancloud
```

This command confirms which AWS account and IAM identity are being used.

Expected output contains:

```json
{
    "UserId": "...",
    "Account": "...",
    "Arn": "arn:aws:iam::<ACCOUNT_ID>:user/cleancloud-local"
}
```

The important validation is that the returned ARN belongs to the dedicated CleanCloud IAM identity rather than an unintended administrator or personal identity.

---

# 8. Step 3 — Install CleanCloud

CleanCloud was installed locally using `pipx`.

The AWS provider extra was installed with:

```bash
pipx install "cleancloud[aws]"
```

The installation completed successfully.

The installed version was then checked with:

```bash
cleancloud --version
```

The environment reported:

```text
cleancloud 1.32.0
Python 3.12.2
Providers: aws
```

CleanCloud is an existing open-source cloud-hygiene scanner.

This project does not claim ownership of or development of CleanCloud itself. The project uses the CleanCloud CLI as the scanning engine and builds an AWS-focused reporting and automation workflow around it.

### Screenshot — CleanCloud Installation

<img width="880" height="316" alt="Screenshot 2026-09-06 122425" src="https://github.com/user-attachments/assets/e7e4a055-48f9-40e4-aa12-0e0678fb9b37" />


---

# 9. Step 4 — Run CleanCloud Doctor

Before running the AWS scan, the environment was validated with:

```bash
cleancloud doctor --provider aws --profile cleancloud
```

The doctor command checks:

- AWS credential resolution
- Authentication method
- AWS account identity
- Region availability
- Required read-only permissions

This is an important step because it prevents troubleshooting the scanner when the actual problem is authentication or IAM permissions.

---

# 10. CleanCloud Doctor — Authentication

The CleanCloud doctor successfully created an AWS session.

The output confirmed:

```text
AWS session created successfully
```

The authentication method was detected as:

```text
AWS CLI Profile
```

The configured IAM identity was also detected successfully.

### Screenshot — Authentication Validation

<img width="1621" height="1008" alt="Screenshot 2026-09-06 122447" src="https://github.com/user-attachments/assets/4cc234c3-64bc-48b0-9d9d-0c685995229f" />

<img width="1691" height="642" alt="Screenshot 2026-09-06 122510" src="https://github.com/user-attachments/assets/a45c047c-220c-45ac-ad0d-73a2c08451e9" />


---

# 11. CleanCloud Doctor — Permission Validation

CleanCloud then validated the AWS read-only permissions required by the scanner.

The checks included permissions for services such as:

```text
EC2
EBS
RDS
Redshift
OpenSearch
Elastic Load Balancing
CloudWatch Logs
CloudWatch
S3
CloudTrail
```

The permission validation completed successfully.

The validation summary reported:

```text
Authentication: AWS CLI Profile
Security Grade: ACCEPTABLE
Permissions Tested: 23/23 passed

AWS ENVIRONMENT READY FOR CLEANCLOUD
```

This confirms that the configured scanning identity was able to perform the tested read-only operations.

### Screenshot — Permission Validation
---

# 12. Region Scope

The CleanCloud doctor output showed:

```text
Active Region: us-east-1
```

It also explained that the doctor validates permissions for the active region.

For a complete scan across active regions, the command recommended by the tool is:

```bash
cleancloud scan --provider aws --all-regions
```

The actual scan therefore used the `--all-regions` option.

---

# 13. Step 5 — Run the AWS Multi-Region Scan

The scan was executed using:

```bash
cleancloud scan \
    --provider aws \
    --profile cleancloud \
    --all-regions
```

The scanner automatically detected AWS regions containing relevant resources.

The scan detected:

```text
ap-south-1
us-east-1
```

Both regions were scanned.

The scanner output showed:

```text
Found 2 active regions:
    ap-south-1
    us-east-1
```

---

# 14. AWS Rules Evaluated

The scan evaluated 15 AWS hygiene rules.

The rules covered areas including:

```text
CloudWatch Logs infinite retention
Old EBS snapshots
Unattached EBS volumes
Old AMIs
Unused Elastic IPs
Detached ENIs
Stopped EC2 instances
Idle NAT Gateways
Unused Security Groups
Idle Load Balancers
Idle OpenSearch domains
Idle RDS instances
Old RDS snapshots
Idle Redshift clusters
Untagged resources
```

Not every rule produced a finding.

A rule being evaluated does not mean a corresponding resource exists or is necessarily problematic.

---

# 15. Initial Scan Results

The initial scan produced:

```text
Total findings: 8
Rules evaluated: 15
Regions scanned: 2
```

Risk distribution:

```text
Low:     6
Medium:  2
```

Confidence distribution:

```text
High:    2
Medium:  6
```

Regions:

```text
ap-south-1
us-east-1
```

### Screenshot — Initial Findings

<img width="1783" height="1017" alt="Screenshot 2026-09-06 123257" src="https://github.com/user-attachments/assets/607c06b8-e8ed-4b47-8aed-4e2d13119965" />
<img width="1918" height="1002" alt="Screenshot 2026-09-06 123308" src="https://github.com/user-attachments/assets/0878967e-902b-4afa-9f6b-511771ecaaf2" />
<img width="1911" height="993" alt="Screenshot 2026-09-06 123325" src="https://github.com/user-attachments/assets/94b22844-29c9-4df5-8f45-2c344168d4b0" />
<img width="1853" height="921" alt="Screenshot 2026-09-06 123407" src="https://github.com/user-attachments/assets/025dd9cc-180e-42c3-b98d-b77b9b11ffe7" />



---

# 16. Security Group Findings

The scan detected several:

```text
Unused security group review candidate
```

findings.

Examples included:

```text
launch-wizard-1
launch-wizard-2
launch-wizard-3
```

The scanner reported:

```text
Attached ENI Count: 0
Referenced by Other Security Group: False
```

These findings should be interpreted as **review candidates**, not automatic deletion recommendations.

An unused security group does not necessarily represent direct monthly cost savings.

It can instead represent:

- Resource hygiene
- Configuration cleanup
- Governance improvement
- Reduced infrastructure clutter

---

# 17. Security Group Validation

Before removing any security group, additional validation should be performed.

## 17.1 Check Network Interfaces

Run:

```bash
aws ec2 describe-network-interfaces \
    --filters Name=group-id,Values=<SECURITY_GROUP_ID> \
    --region <REGION> \
    --profile cleancloud
```

This verifies whether the security group is attached to network interfaces.

---

## 17.2 Check Security Group References

A security group can be referenced by another security group.

CleanCloud reports:

```text
referenced_by_other_sg
```

If this value is:

```text
true
```

the resource must be investigated before any removal.

---

## 17.3 Check Terraform

Some of the security groups identified by the scan contain tags such as:

```text
ManagedBy = Terraform
```

When Terraform manages a resource, manually deleting it from AWS may create infrastructure drift.

The correct approach is to review:

```text
Terraform configuration
Terraform state
Application dependencies
AWS resource references
```

before making a change.


---

# 18. S3 Untagged Resource Finding

The scan also detected an untagged S3 bucket.

The finding was:

```text
Untagged S3 bucket
```

The bucket reported by CleanCloud was:

```text
viren-client-onboarding-tf-state
```

The finding reported:

```text
Risk: Medium
Confidence: High
Current tag count: 0
```

The scanner reason was:

```text
No current tags found in authoritative tag source
```

The bucket should not be deleted simply because it is untagged.

The resource should first be validated to determine:

- Its purpose
- Whether it is actively used
- Whether it is Terraform-related
- Its ownership
- Whether tags are required by the organization's standards

---

# 19. S3 Validation

## 19.1 Check Tags

```bash
aws s3api get-bucket-tagging \
    --bucket <BUCKET_NAME> \
    --profile cleancloud
```

---

## 19.2 Check Bucket Location

```bash
aws s3api get-bucket-location \
    --bucket <BUCKET_NAME> \
    --profile cleancloud
```

---

## 19.3 Check Bucket Contents

```bash
aws s3 ls s3://<BUCKET_NAME> \
    --profile cleancloud
```

These checks help determine whether the bucket is actively used before deciding what remediation, if any, is appropriate.

---

# 20. Important Observation — Findings Are Not Automatic Deletion Commands

A cloud scanner should be treated as a detection and analysis tool.

For example:

```text
CleanCloud
    |
    v
Security group appears unused
```

does **not** automatically mean:

```text
Delete security group
```

The safe workflow is:

```text
CleanCloud Finding
        |
        v
Validate AWS Resource
        |
        v
Check Dependencies
        |
        v
Check Terraform / IaC
        |
        v
Approve Remediation
        |
        v
Make Change
        |
        v
Re-scan
```

---

# 21. Step 6 — Save Raw Findings as JSON

The CleanCloud scan was configured to save its raw output as:

```text
reports/findings.json
```

The JSON file contains the structured scanner results.

The raw JSON is retained because it can be used as the source data for future automation.

The workflow is:

```text
CleanCloud
    |
    v
findings.json
```

---

# 22. Why JSON Is Retained

JSON is useful because it is:

- Machine-readable
- Structured
- Easy to process with Python
- Suitable for automation
- Useful for future dashboards
- Useful for historical comparisons
- Useful for CI/CD integrations

The original CleanCloud JSON output remains the source of truth for the generated report.

---

# 23. Step 7 — Automate JSON to CSV Conversion

The project uses a custom Python script:

```text
scripts/generate_report.py
```

The purpose of this script is to automatically transform the CleanCloud JSON output into a human-readable CSV file.

The flow is:

```text
findings.json
      |
      v
generate_report.py
      |
      v
aws-cloud-hygiene-report.csv
```

The generated report is:

```text
reports/aws-cloud-hygiene-report.csv
```

---

# 24. CSV Report Fields

The CSV report contains fields including:

| Field | Purpose |
|---|---|
| Region | AWS region |
| Resource Type | AWS resource category |
| Resource ID | AWS resource identifier |
| Resource Name | Human-readable resource name |
| Finding | CleanCloud finding |
| Risk | Risk level |
| Confidence | Scanner confidence |
| Attached ENIs | ENI attachment information |
| Referenced by Other SG | Security group dependency information |
| VPC ID | Associated VPC |
| Age (days) | Resource age when available |
| Estimated Monthly Cost | Estimated cost when provided |
| Tags | Resource tags |
| Recommendation | Suggested validation action |
| Detected At | Finding timestamp |

This makes the scanner output easier to review without manually reading the JSON structure.

---

# 25. Step 8 — Automate the Complete Workflow with Bash

The complete workflow is automated through:

```text
run-scan.sh
```

The command:

```bash
./run-scan.sh
```

performs the following steps:

```text
1. Locate project directory
        |
        v
2. Create reports directory
        |
        v
3. Run CleanCloud AWS scan
        |
        v
4. Generate findings.json
        |
        v
5. Run generate_report.py
        |
        v
6. Generate CSV report
        |
        v
7. Verify CSV exists
        |
        v
8. Display successful report generation
```

---

# 26. End-to-End Automation

The implemented workflow is:

```text
                 ./run-scan.sh
                       |
                       v
                CleanCloud Scan
                       |
                       v
                AWS Multi-Region
                       |
                       v
                 findings.json
                       |
                       v
             generate_report.py
                       |
                       v
            CSV Hygiene Report
                       |
                       v
               Review Findings
```

This removes the need to manually run the JSON-to-CSV conversion after every scan.

---

# 27. Successful Automated Execution

The automated script was successfully executed.

The output showed:

```text
CleanCloud scan completed successfully.

Generating CSV report...

CSV report generated successfully:
C:\Users\Viren\aws-cost-optimization-cleancloud\reports\aws-cloud-hygiene-report.csv

Total findings exported: 8

Reports generated:
    JSON : reports/findings.json
    CSV  : reports/aws-cloud-hygiene-report.csv
```

### Screenshot — Automated Scan and CSV Generation

<img width="1482" height="492" alt="Screenshot 2026-09-06 132630" src="https://github.com/user-attachments/assets/c07e0822-029f-498d-be79-9311de184bbd" />



This confirms that:

1. CleanCloud completed the AWS scan.
2. The JSON file was generated.
3. The Python converter executed successfully.
4. Eight findings were exported.
5. The CSV report was created.

---

# 28. Verify Generated Reports

The generated reports were verified with:

```bash
cd reports
ls -la
```

The directory contains:

```text
aws-cloud-hygiene-report.csv
findings.json
```

### Screenshot — Generated Reports

<img width="1702" height="738" alt="Screenshot 2026-09-06 132329" src="https://github.com/user-attachments/assets/dddad5f6-5ef8-4f52-b1ca-0ff0e6204ac5" />


The final output directory is therefore:

```text
reports/
├── findings.json
└── aws-cloud-hygiene-report.csv
```

---

# 29. Initial Scan Summary

The current implementation produced:

| Metric | Result |
|---|---:|
| AWS Regions Scanned | 2 |
| Regions | ap-south-1, us-east-1 |
| Rules Evaluated | 15 |
| Total Findings | 8 |
| Low Risk | 6 |
| Medium Risk | 2 |
| High Risk | 0 |
| High Confidence | 2 |
| Medium Confidence | 6 |

The findings included unused-security-group review candidates and an untagged S3 bucket finding.

---

# 30. Findings vs. Direct Cost Savings

An important part of this project is distinguishing cloud hygiene from measurable cost savings.

For example:

```text
Unused Security Group
```

can improve:

- Cloud hygiene
- Governance
- Resource management
- Infrastructure visibility

but it does not necessarily reduce the AWS monthly bill.

Therefore, the project does not claim cost savings simply because CleanCloud reports a finding.

Direct cost optimization opportunities can include resources such as:

```text
Unattached EBS volumes
Old snapshots
Unused Elastic IPs
Stopped EC2 instances
Idle NAT Gateways
Idle Load Balancers
Idle RDS instances
Idle OpenSearch domains
Idle Redshift clusters
```

The current scan did not report findings for these categories.

Therefore, no unsupported savings figure is claimed from the current scan.

---

# 31. Remediation Strategy

The project follows a controlled remediation lifecycle.

## Phase 1 — Detect

CleanCloud identifies a potential issue.

```text
AWS Resource
    |
    v
CleanCloud
    |
    v
Finding
```

## Phase 2 — Validate

The resource is investigated.

Possible checks include:

```text
AWS CLI
Terraform
Application dependencies
Network interfaces
Security group references
Resource activity
Tags
Ownership
```

## Phase 3 — Remediate

After validation, the resource may be:

- Removed
- Tagged
- Updated
- Right-sized
- Migrated
- Managed through Terraform

## Phase 4 — Verify

Run the scanner again:

```bash
./run-scan.sh
```

The finding should disappear if the remediation resolves the detected condition.

## Phase 5 — Automate

After the workflow has been validated, it can be integrated with:

```text
GitHub Actions
AWS OIDC
Scheduled scans
CI/CD policy checks
Multi-account scanning
Central reporting
```

---

# 32. Terraform-Aware Remediation

When CleanCloud identifies a resource with:

```text
ManagedBy = Terraform
```

the resource should be checked against Infrastructure as Code.

The preferred workflow is:

```text
CleanCloud Finding
        |
        v
Identify Terraform Resource
        |
        v
Review Terraform Configuration
        |
        v
Review Terraform State
        |
        v
Modify IaC
        |
        v
terraform plan
        |
        v
terraform apply
        |
        v
CleanCloud Rescan
```

This helps prevent infrastructure drift.

---

# 33. Security Model

The scanner identity is intentionally read-only.

The scanning identity should not be granted destructive permissions such as:

```text
ec2:TerminateInstances
ec2:DeleteSecurityGroup
ec2:DeleteVolume
s3:DeleteBucket
rds:DeleteDBInstance
```

Scanning and remediation are separate responsibilities.

```text
Scanner
   |
   +-- Read-only
   |
   +-- Detect
   |
   +-- Report

Remediation Process
   |
   +-- Controlled write access
   |
   +-- Approval
   |
   +-- Change
```

This separation reduces the risk of accidental destructive operations.

---

# 34. Credential Security

Never commit the following files or information:

```text
AWS access keys
AWS secret keys
AWS session tokens
~/.aws/credentials
~/.aws/config
Private keys
Terraform state containing secrets
.env files
```

The project `.gitignore` should protect sensitive local files.

Example:

```gitignore
.aws/
credentials
config

.env
.env.*

*.pem
*.key

.terraform/
*.tfstate
*.tfstate.*

reports/*.json
reports/*.csv
```

---

# 35. GitHub Publishing Checklist

Before pushing the project to GitHub:

### Credentials

- [ ] Remove AWS credentials from screenshots
- [ ] Remove AWS credentials from files
- [ ] Verify no `.aws` directory is committed
- [ ] Verify no secret keys exist in Git history
- [ ] Rotate any credential that was accidentally exposed

### AWS Information

Review screenshots and reports for:

- [ ] AWS account IDs
- [ ] IAM user identifiers
- [ ] Resource IDs
- [ ] Bucket names
- [ ] Internal client names
- [ ] Private IP addresses
- [ ] Internal URLs
- [ ] Sensitive tags

### Generated Reports

Because `findings.json` and the CSV may contain AWS-specific resource information, consider keeping generated reports local and committing only:

```text
reports/.gitkeep
```

instead of real production/account-specific reports.

---

# 36. Current Project Status

## Completed

- [x] Dedicated AWS IAM scanning identity
- [x] Read-only IAM policy
- [x] AWS CLI profile
- [x] AWS identity validation
- [x] CleanCloud installation
- [x] CleanCloud version verification
- [x] CleanCloud doctor validation
- [x] Read-only permission validation
- [x] Multi-region AWS scan
- [x] JSON findings generation
- [x] Python JSON-to-CSV converter
- [x] Bash scan automation
- [x] Automated CSV generation
- [x] Generated report verification
- [x] Initial findings review

## In Progress

- [ ] Validate individual findings
- [ ] Review Terraform dependencies
- [ ] Define tagging standards
- [ ] Configure CleanCloud rules
- [ ] Document remediation decisions
- [ ] Measure actual cost savings where applicable

## Planned

- [ ] Scheduled scans
- [ ] GitHub Actions integration
- [ ] AWS OIDC authentication
- [ ] CI/CD policy enforcement
- [ ] Historical finding comparison
- [ ] Reporting/dashboard improvements
- [ ] Multi-account AWS scanning
- [ ] AWS Organizations integration

---

# 37. Future CI/CD Architecture

The next stage can move the local workflow into GitHub Actions.

Future architecture:

```text
                    GitHub
                       |
                       v
               GitHub Actions
                       |
                       v
                  AWS OIDC
                       |
                       v
             Read-Only IAM Role
                       |
                       v
                  CleanCloud
                       |
              +--------+--------+
              |                 |
              v                 v
       findings.json       Policy Check
              |
              v
        CSV / Reports
```

The objective is to avoid storing long-lived AWS access keys in GitHub Actions.

---

# 38. Future Multi-Account Architecture

The project can later be extended to multiple AWS accounts.

Example:

```text
                  AWS Organization
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
      Account A      Account B      Account C
          |              |              |
          +--------------+--------------+
                         |
                         v
                  Central Scanner
                         |
                         v
                  Central Reports
```

This can provide centralized cloud-hygiene visibility across multiple AWS environments.

---

# 39. Lessons Learned

## Least Privilege

A dedicated read-only IAM identity is safer than using an administrator identity for scanning.

## Multi-Region Awareness

AWS resources can exist across multiple regions, so limiting a scan to one region may miss resources.

## Detection Is Not Remediation

A finding should be investigated before making a change.

## Infrastructure as Code Awareness

Terraform-managed resources should be considered carefully before manual AWS changes.

## Automation

Combining CleanCloud, Bash, and Python removes repetitive manual reporting work.

## Structured Reporting

JSON is useful for machine processing while CSV is easier for human review.

## Cost Optimization Requires Measurement

A hygiene finding should not automatically be represented as a monthly cost saving.

---

# 40. Final End-to-End Workflow

The implementation now follows:

```text
                         AWS
                          |
                          v
                  Dedicated IAM User
                          |
                          v
                    AWS CLI Profile
                          |
                          v
                       CleanCloud
                          |
                          v
                  Environment Doctor
                          |
                          v
                  Permission Validation
                          |
                          v
                  Multi-Region Scan
                          |
                          v
                    findings.json
                          |
                          v
                 generate_report.py
                          |
                          v
              aws-cloud-hygiene-report.csv
                          |
                          v
                    Review Findings
                          |
                          v
                  Validate Resources
                          |
                          v
                 Terraform / AWS Review
                          |
                          v
                      Remediate
                          |
                          v
                       Re-scan
                          |
                          v
                        Verify
```

---

# 41. One-Command Execution

Once the environment is configured, the complete local scan and reporting workflow can be executed with:

```bash
./run-scan.sh
```

The command performs:

```text
CleanCloud AWS Scan
        ↓
JSON Findings
        ↓
Python Report Generation
        ↓
CSV Report
        ↓
CSV Verification
```

The resulting reports are:

```text
reports/findings.json
reports/aws-cloud-hygiene-report.csv
```

---

# 42. Conclusion

This implementation establishes a practical AWS cloud-hygiene workflow using CleanCloud.

The project currently demonstrates:

- Read-only AWS access
- IAM least-privilege principles
- AWS CLI profile-based authentication
- Environment and permission validation
- Multi-region AWS scanning
- Structured JSON findings
- Automated JSON-to-CSV reporting
- Bash-based end-to-end automation
- Safe finding interpretation
- Terraform-aware remediation planning

The next phase is to validate the detected resources individually, identify genuine cleanup opportunities, distinguish hygiene improvements from measurable cost savings, and then extend the workflow toward scheduled scanning, CI/CD integration, OIDC authentication, and multi-account AWS environments.
