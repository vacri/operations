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
