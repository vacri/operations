AWS Utility Scripts
==================

These scripts are all for interaction with AWS, and generally assume you have the following:
* valid AWS keys on the running user
  * scripts intended to run within EC2 assume environmental/role-based keys and generally don't use profiles
* aws cli tool installed
* boto3 installed (AWS python bindings)

| thing | function |
| --- | --- |
| acm-fetch-dns-edits     | find the DNS edits needed for a new ACM record |
| aws-acm-dehydrated-hook | allows Dehydrated (Lets Encrypt agent) to upload certs to ACM |
| aws-log-archiver        | collates squillions of ELB and Cloudfront logfiles into single archive files |
| bashrc_aws_mfa          | bash alias to ease mfa-enabling awscli |
| ec2-instance-volume-snapshot | snapshot (backup) all EC2 volumes with given tag+value |
| ec2-remake-lc | automate updating an ASG LC - manually updating is prone to error |
| https_expiry_checker.py | AWS Lambda code for cert expiry checking |
| r53-ns-compare          | Discover if an R53 zone is live DNS or not |
| r53-set-record          | Make single r53 records |
| rds-db-backup           | backs up individual databases from RDS mysql to s3 (native RDS backups = whole machine) |
| rds-db-backup-tester    | tests mysql backup files by installing to a temp db |
| rds-db-init             | creates empty dbs on RDS mysql, using lookups from Parameter Store |
| route53_backup.py       | AWS Lambda code to backup route53 zones to s3 |
