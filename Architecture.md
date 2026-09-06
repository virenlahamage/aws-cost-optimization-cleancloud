                    AWS Account
                         |
                         |
                  Read-Only IAM User
                         |
                         |
                    AWS CLI Profile
                         |
                         v
                  +---------------+
                  |   CleanCloud   |
                  |   AWS Scanner  |
                  +-------+-------+
                          |
                          | JSON
                          v
                  reports/findings.json
                          |
                          v
                +----------------------+
                | generate_report.py   |
                | JSON → CSV converter |
                +----------+-----------+
                           |
                           | CSV
                           v
             reports/aws-cloud-hygiene-report.csv
