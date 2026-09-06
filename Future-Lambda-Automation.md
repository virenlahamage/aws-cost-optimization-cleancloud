                 EventBridge
              Every 15 Days
                    |
                    v
                 Lambda
                    |
                    v
             CleanCloud Scan
                    |
                    v
          Read-Only AWS Permissions
                    |
          +---------+---------+
          |                   |
          v                   v
   findings.json          Policy Check
          |
          v
      CSV Report
          |
          v
       S3 Bucket
          |
          v
   Historical Reports
