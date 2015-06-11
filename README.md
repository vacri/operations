Operations Scripts
==================

All scripts are non-destructive when run without any arguments (and usually give 'usage' info). Scripts from various $DAYJOB, with identifying crap removed. They're written for a Debian/Ubuntu environment

As most of these scripts are sanitised, there are some variables at the start that will need customisation (usually a placeholder in capitals will indicated required vars)

| thing | function |
| archive-gmail     | get a zipped .mbox of your gmail |
| bash.boilerplate  | boilerplate for bash scripts |
| check-elasticsearch | nagios check for ElasticSearch status |
| ddvpn-syd         | call with sudo with OpenConnect installed, connects to your Dimension Data Sydney VPN |
| deploy-s3-site    | uploads repos/local dirs to s3 bucket websites, gzipping appropriate files |
| ec2-create-rolling-snapshot | snapshots EC2 volumes, intended as a daily cronjob |
| kvm-backup        | backup KVM virtual machines that aren't snapshottable (requires VM downtime) |
| git-counter       | compare contributors' lines of code for a repo |
| info.php | php info snippet for testing webserving works |
| init.boilerplate.centos | init script template for ye olde CentOS, which I never want to touch again |
| meat              | read config files without comments or empty lines (just the 'meat') |
| mmsdump | use mongodump on an MMS-managed mongodb
| mongo-backup      | script for making backup tar.gz's from a local mongo |
| mysql-meta | grab user grants or database metadata without having to remember the sql query to do so... |
| mysql-tablemigrate | copy a monotonically-increasing large database table (200GB)
| nginx_[dis|en]site |- make those nginx symlinks! |
| send-sms-global   | sends SMSes via SMS Global |
| snappywrapper     | use the ec2 rolling snapshotter  within AWS, using instance role-based perms |
| unifi-prune.js    | en-smallerise the mongo DB used by the unifi controller |
| yank              | script to overcome Docker's shortcomings for deployment |
