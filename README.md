Operations Scripts
==================

All scripts are non-destructive when run without any arguments (and usually give 'usage' info). Scripts from various $DAYJOB, with identifying crap removed. They're written for a Debian/Ubuntu environment

As most of these scripts are sanitised, there are some variables at the start that will need customisation (usually a placeholder in capitals will indicated required vars)

| thing | function |
| --- | --- |
| archive-gmail     | get a zipped .mbox of your gmail |
| bash.boilerplate  | boilerplate for bash scripts |
| check-elasticsearch | nagios check for ElasticSearch status |
| check-redirects   | confirm http redirects for a list of domains |
| ddvpn-syd         | call with sudo with OpenConnect installed, connects to your Dimension Data Sydney VPN |
| deploy-s3-site    | uploads repos/local dirs to s3 bucket websites, gzipping appropriate files |
| di                | get shell on a running docker container |
| ec2-create-rolling-snapshot | snapshots EC2 volumes, intended as a daily cronjob |
| kvm-backup        | backup KVM virtual machines that aren't snapshottable (requires VM downtime) |
| gatekeeper        | tar/zipfile deployer for autoscaled VMs, see README in subdir |
| git-counter       | compare contributors' lines of code for a repo |
| grafana-backup-s3 | backs up grafana db (settings) to s3 |
| https-code-checker | checks http codes for http/https on given domains |
| info.php | php info snippet for testing webserving works |
| init.boilerplate.centos | init script template for ye olde CentOS, which I never want to touch again |
| json2yaml         | convert json to human-readable yaml |
| ldap-backup-s3    | backup an ldap namespace to s3 |
| meat              | read config files without comments or empty lines (just the 'meat') |
| mmsdump | use mongodump on an MMS-managed mongodb
| mongo-backup      | script for making backup tar.gz's from a local mongo |
| mysql-meta | grab user grants or database metadata without having to remember the sql query to do so... |
| mysql-restore-from-s3 | restore mysql from backup file on s3 |
| mysql-tablemigrate | copy a monotonically-increasing large database table (200GB)
| nginx_[dis|en]site |- make those nginx symlinks! |
| prometheus-backup-s3 | backups up prometheus via btrfs snapshots to s3 |
| remove-comments-and-base64-encode | useful for EC2 userdata scripts |
| send-sms-global   | sends SMSes via SMS Global |
| snappywrapper     | use the ec2 rolling snapshotter  within AWS, using instance role-based perms |
| unifi-prune.js    | en-smallerise the mongo DB used by the unifi controller |
| update-openvpn-crl | update openvpn cert revocation list (list older than 90 days = no new cnx) |
| vacri-in-a-box    | ops advice simulator for devs |
| wpengine-copy     | CI script to copy content to an ssh-capable WPEngine install |
| xwiki-backup-s3   | backs up xwiki to s3 (defunct) |
| yaml2json         | convert yaml to human-illegible json|
| yank              | script to overcome Docker's shortcomings for deployment |
